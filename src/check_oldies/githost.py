import dataclasses
import json
import urllib.parse
import urllib.request


@dataclasses.dataclass
class PullRequestInfo:
    number: str
    state: str
    url: str


def PullRequestGetter(platform, host_owner, api_access):
    if platform.lower() == "github":
        klass = GitHubApi
    elif platform.lower() == "gitlab":
        klass = GitLabApi
    else:
        raise ValueError("Unsupported Git host platform." "")
    return klass(host_owner, api_access)


class GitHubApi:
    authentication_header = 'token'

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
            "Authorization": f"{self.authentication_header} {self.auth_token}",
            "Content-Type": "application/json",
        }
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)  # pylint: disable=consider-using-with
        return json.loads(response.read())


class GitLabApi(GitHubApi):
    authentication_header = 'Bearer'

    def _get_project(self, repo):
        query = {
            "search": f"{repo}",
            "scope": "projects",
        }
        response = self._get(f'{self.api_base_url}/search/', query)
        for project in response:
            if project['name'] == repo:
                return project

        return None

    def get_pull_request(self, repo, branch):
        project = self._get_project(repo)
        if not project:
            return None
        url = f"{self.api_base_url}/projects/{project['id']}/merge_requests"
        # If the branch is linked to more than one pull request,
        # return the most recent one.
        query = {
            "source_branch": f"{branch}",
            "order_by": "created_at",
            "sort": "desc",
        }
        response = self._get(url, query)
        if not response:
            return None
        info = response[0]
        return PullRequestInfo(
            number=info["iid"],
            state=info["state"],
            url=info["web_url"],
        )
