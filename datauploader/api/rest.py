import json
import requests

# sort order is most recently created first
# max page size = 100 (may not be respected or vary, but this is the max max)
# https://developer.github.com/v3/#pagination


GITHUB_RATE_LIMIT_ENDPOINT = "https://api.github.com/rate_limit"
GITHUB_REPOS_ENDPOINT = "https://api.github.com/user/repos?sort=created&per_page=100"


def get_auth_header(github_access_token):
    auth_header = {"Authorization": "Bearer " + github_access_token}
    return auth_header


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
