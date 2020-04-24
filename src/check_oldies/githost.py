import dataclasses
import json
import urllib.parse
import urllib.request


@dataclasses.dataclass
class PullRequestInfo:
    number: str
    state: str
    url: str


def PullRequestGetter(host_owner, api_access):
    if api_access.platform.lower() == "github":
        klass = GitHubApi
    else:
        raise ValueError("Unsupported Git host platform." "")
    return klass(host_owner, api_access)


class GitHubApi:
    def __init__(self, host_owner, api_access):
        self.api_base_url = api_access.api_base_url
        self.owner = host_owner
        self.auth_token = api_access.auth_token

    def get_pull_request(self, repo, branch):
        url = f"{self.api_base_url}/repos/{self.owner}/{repo}/pulls"
        # If the branch is linked to more than one pull request,
        # return the most recent one.
        query = {
            "head": f"{self.owner}:{branch}",
            "state": "all",
            "sort": "created",
            "direction": "desc",
        }
        response = self._get(url, query)
        if not response:
            return None
        info = response[0]
        return PullRequestInfo(
            number=info["number"],
            state=info["state"],
            url=info["html_url"],
        )

    def _get(self, url, query=None):
        if query:
            url += "?" + urllib.parse.urlencode(query)
        headers = {
            "Authorization": f"token {self.auth_token}",
            "Content-Type": "application/json",
        }
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        return json.loads(response.read())
