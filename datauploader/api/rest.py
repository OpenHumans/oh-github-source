import json
import requests


GITHUB_RATE_LIMIT_ENDPOINT = "https://api.github.com/rate_limit"


def get_rate_limit_remaining(github_access_token, type="core"):
    """ Get the rate limit remaining and the reset time (in seconds from epoch format) as a tuple.
     The query itself does not decrement the available
    credit remaining.

    https://developer.github.com/v3/rate_limit/

    """

    auth_header = {"Authorization": "Bearer " + github_access_token}
    response = requests.get(GITHUB_RATE_LIMIT_ENDPOINT, headers=auth_header)
    rate_limit_info = json.loads(response.content)['resources'][type]
    return rate_limit_info['remaining'], rate_limit_info['reset']
