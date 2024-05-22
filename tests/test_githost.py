import os
from unittest import mock

from check_oldies import branches
from check_oldies import githost


FAKE_GITHUB_API_RESPONSE = [
    {
        "number": 1234,
        "state": "open",
        "html_url": "https://github.com/polyconseil/check-oldies/pull/1234",
    },
]


@mock.patch.dict(os.environ, {"TOKEN": "secret"}, clear=True)
def test_github_api(requests_mocker):
    requests_mocker.get(
        "https://api.github.com/repos/polyconseil/check-oldies/pulls",
        json=FAKE_GITHUB_API_RESPONSE,
    )
    api_access = branches.GitHostApiAccessInfo(auth_token_env_var="TOKEN")
    api = githost.GitHubApi("polyconseil", api_access)
    pull_request = api.get_pull_request("check-oldies", "my-branch")
    assert pull_request.number == 1234
    assert pull_request.state == "open"
    assert pull_request.url == "https://github.com/polyconseil/check-oldies/pull/1234"
