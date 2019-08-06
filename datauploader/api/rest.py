import json
import requests


from ohapi import api


from datauploader.api.helpers import write_jsonfile_to_tmp_dir, download_to_json, get_commit_date

# sort order is most recently created first
# max page size = 100 (may not be respected or vary, but this is the max max)
# https://developer.github.com/v3/#pagination


GITHUB_USER_INFO_ENDPOINT = "https://api.github.com/user"
GITHUB_RATE_LIMIT_ENDPOINT = "https://api.github.com/rate_limit"
GITHUB_REPOS_ENDPOINT = "https://api.github.com/user/repos?sort=created&per_page=100"
GITHUB_REPO_COMMITS_ENDPOINT = "https://api.github.com/repos/{}/commits?author={}&per_page=100"


def get_github_data(oh_access_token, gh_access_token, current_date):

    existing_github_data = get_last_synced_data(oh_access_token)
    new_github_data = GithubData.from_API(gh_access_token, existing_github_data)
    full_file_name = write_jsonfile_to_tmp_dir('github.json', new_github_data.to_json())

    return full_file_name


def get_last_synced_data(oh_access_token):
    download_url = get_latest_github_file_url(oh_access_token)
    if download_url:
        existing_data_json = download_to_json(download_url)
        last_data = GithubData.from_json(existing_data_json)
    else:
        last_data = None

    return last_data


def get_latest_github_file_url(oh_access_token):
    member = api.exchange_oauth2_member(oh_access_token)
    download_url = None
    last_updated_at = None
    for dfile in member['data']:
        if 'Github' in dfile['metadata']['tags']:
            if last_updated_at is None or dfile['metadata'].get('updated_at', '') >= last_updated_at:
                last_updated_at = dfile['metadata']['updated_at']
                download_url = dfile['download_url']
    return download_url


def get_auth_header(github_access_token):
    auth_header = {"Authorization": "Bearer " + github_access_token}
    return auth_header


def get_full_names_from_repos(repos):
    return [repo['full_name'] for repo in repos]


def get_rate_limit_remaining(github_access_token, type="core"):
    """ Get the rate limit remaining and the reset time (in seconds from epoch format) as a tuple.
     The query itself does not decrement the available
    credit remaining.

    https://developer.github.com/v3/rate_limit/

    """

    auth_header = get_auth_header(github_access_token)
    response = requests.get(GITHUB_RATE_LIMIT_ENDPOINT, headers=auth_header)
    rate_limit_info = json.loads(response.content)['resources'][type]
    return rate_limit_info['remaining'], rate_limit_info['reset']


def get_user_info(github_access_token):
    auth_header = get_auth_header(github_access_token)
    response = requests.get(GITHUB_USER_INFO_ENDPOINT, headers=auth_header)
    return json.loads(response.content)


def get_user_repos(github_access_token):
    results = []
    cnt = 0
    url = GITHUB_REPOS_ENDPOINT
    while True:
        cnt += 1
        response = requests.get(url, headers=get_auth_header(github_access_token))
        results += json.loads(response.content)
        next = response.links.get('next')
        if not next:
            break
        else:
            url = next['url']
    #print("Called the api {} times".format(cnt))
    return results


def get_repo_commits_for_user(github_access_token, repo, username, sync_after_date):
    results = []
    cnt = 0
    url = GITHUB_REPO_COMMITS_ENDPOINT.format(repo, username)
    # commits are fetched chronologically
    latest_commit_date = None

    reached_previous_data = False

    while not reached_previous_data:
        cnt += 1
        response = requests.get(url, headers=get_auth_header(github_access_token))
        commits = json.loads(response.content)

        if latest_commit_date is None and len(commits) > 0:
            # github returns the data in descending chronological order
            # date is in the format 2014-05-09T15:14:07Z
            latest_commit_date = get_commit_date(commits[0])

        if sync_after_date is not None:
            for idx, commit in enumerate(commits):
                commit_date = get_commit_date(commit)
                # this may not handle rebases/history rewrites 100% correctly
                # is good effort for gathering our commit histories <:o)
                if commit_date <= sync_after_date:
                    print("reached existing data at idx {}".format(idx))
                    print("will only add {} to existing".format(commits[:idx]))
                    reached_previous_data = True
                    commits = commits[:idx]
                    break


        results += commits
        # if results['type'] == 'PushEvent'
        # results[0]['payload']['commits'][0]['message']
        next = response.links.get('next')
        if not next:
            break
        else:
            url = next['url']
    #print("Called the api {} times".format(cnt))
    return results, latest_commit_date


class GithubData(object):

    def __init__(self, repo_data, metadata):
        self.repo_data = repo_data
        self.metadata = metadata


    def get_last_commit_date_for_repo(self, repo):

        if repo in self.repo_data:
            return self.repo_data[repo]['last_commit_date']
        return None

    def get_commits_for_repo(self, repo):

        if repo in self.repo_data:
            return self.repo_data[repo]['commits']
        return []


    def __repr__(self):
        return str(self.metadata) + '\n' + str(self.repo_data.keys())

    @classmethod
    def from_API(self, token, existing_data):

        print("Starting rate limit status:")
        print(get_rate_limit_remaining(token))
        user_info = get_user_info(token)
        username = user_info.get('login')
        repos = get_user_repos(token)
        repo_names = get_full_names_from_repos(repos)

        repo_data = {}
        for repo_name in repo_names:
            print("Fetching new commits for {}".format(repo_name))

            if existing_data:
                last_existing_commit_date = existing_data.get_last_commit_date_for_repo(repo_name)
            else:
                last_existing_commit_date = None

            repo_commits, latest_date = get_repo_commits_for_user(token, repo_name, username, sync_after_date=last_existing_commit_date)
            print("Fetched {} new commits".format(len(repo_commits)))

            if existing_data:
                repo_commits = repo_commits + existing_data.get_commits_for_repo(repo_name)

            repo_data[repo_name] = {"commits": repo_commits, "last_commit_date": latest_date,
                                    "num_commits": len(repo_commits)}

        metadata = {"user_info": user_info, "num_repos": len(repos)}

        print("Ending rate limit status:")
        print(get_rate_limit_remaining(token))
        return GithubData(repo_data, metadata)

    @classmethod
    def from_json(self, json_data):
        metadata = json_data['metadata']
        return GithubData(repo_data=json_data['repo_data'], metadata=metadata)

    def to_json(self):
        return {
            "repo_data": self.repo_data,
            "metadata": self.metadata
        }
