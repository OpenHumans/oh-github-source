import json
import requests


from datauploader.api.helpers import write_jsonfile_to_tmp_dir

# sort order is most recently created first
# max page size = 100 (may not be respected or vary, but this is the max max)
# https://developer.github.com/v3/#pagination


GITHUB_USER_INFO_ENDPOINT = "https://api.github.com/user"
GITHUB_RATE_LIMIT_ENDPOINT = "https://api.github.com/rate_limit"
GITHUB_REPOS_ENDPOINT = "https://api.github.com/user/repos?sort=created&per_page=100"
GITHUB_REPO_COMMITS_ENDPOINT = "https://api.github.com/repos/{}/commits?author={}&per_page=100"


def get_github_data(oh_access_token, gh_access_token, current_date):

    start_dt = None # TODO: how to get the appropriate start date
    github_data = GithubData.from_API(gh_access_token, start_dt, current_date)
    full_file_name = write_jsonfile_to_tmp_dir('github.json', github_data.to_json())

    return full_file_name


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
    while(True):
        cnt+=1
        response = requests.get(url, headers=get_auth_header(github_access_token))
        results += json.loads(response.content)
        next = response.links.get('next')
        if not next:
            break
        else:
            url = next['url']
    #print("Called the api {} times".format(cnt))
    return results


def get_repo_commits_for_user(github_access_token, repo, username):
    results = []
    cnt = 0
    url = GITHUB_REPO_COMMITS_ENDPOINT.format(repo, username)
    while(True):
        cnt+=1
        response = requests.get(url, headers=get_auth_header(github_access_token))
        results += json.loads(response.content)
        # if results['type'] == 'PushEvent'
        # results[0]['payload']['commits'][0]['message']
        next = response.links.get('next')
        if not next:
            break
        else:
            url = next['url']
    #print("Called the api {} times".format(cnt))
    return results


class GithubData(object):

    def __init__(self, repo_data, metadata):
        self.repo_data = repo_data
        self.metadata = metadata


    def __repr__(self):
        return str(self.metadata) + '\n' + str(self.repo_data.keys())

    @classmethod
    def from_API(self, token, start_dt, end_dt):
        # TODO handle stopping once we reach already synced data
        print("Starting rate limit status:")
        print(get_rate_limit_remaining(token))
        username = get_user_info(token).get('login')
        repos = get_user_repos(token)
        repo_names = get_full_names_from_repos(repos)

        repo_data = {}
        for repo_name in repo_names:
            print("Fetching commits for {}".format(repo_name))
            repo_commits = get_repo_commits_for_user(token, repo_name, username)
            print("Fetched {} commits".format(len(repo_commits)))
            repo_data[repo_name] = {"commits": repo_commits}

        metadata = {"username": username, "num_repos": len(repos)}

        print("Ending rate limit status:")
        print(get_rate_limit_remaining(token))
        return GithubData(repo_data, metadata)

    @classmethod
    def from_json(self, json_data):
        pass

    def to_json(self):
        return {
            "repo_data": self.repo_data,
            "metadata": self.metadata
        }
