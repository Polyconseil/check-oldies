import dataclasses
import datetime
import os
import pathlib
import re
import typing
import urllib.parse

from . import commands
from . import githost


TODAY = datetime.date.today()
SSH_GIT_URL = re.compile('(?P<user>.+)@(?P<host>.+):(?P<path>.+)')
DEFAULT_API_URL = "https://api.github.com"


@dataclasses.dataclass
class GitHostApiAccessInfo:
    api_base_url: str = DEFAULT_API_URL
    auth_token_file: str = None
    auth_token_env_var: str = None

    def __post_init__(self):
        self.auth_token = self.get_auth_token()

    def get_auth_token(self):
        if self.auth_token_file:
            return pathlib.Path(self.auth_token_file).expanduser().read_text(encoding='utf-8').strip()
        if self.auth_token_env_var:
            return os.environ[self.auth_token_env_var]
        raise ValueError(
            "Missing configuration to get authentication token for Git host API."
        )


@dataclasses.dataclass
class Config:
    platform: str = None
    path: str = "."
    max_age: int = 90

    colorize_errors: bool = True
    xunit_file: str = None

    calm_branches: typing.Sequence = ("gh-pages", "master", "main", "prod", "maint(enance)?/.*")
    ignore_branches_without_pull_request: bool = False

    host_api_access: dict = None

    # Cannot be configured, but is automatically filled in instead. Default value is irrelevant and only here to
    # initialize the field.
    host: str = dataclasses.field(default=None, init=False)
    host_owner: str = dataclasses.field(default=None, init=False)
    repo_name: str = dataclasses.field(default=None, init=False)

    def __post_init__(self):
        if self.host_api_access:
            self.host_api_access = GitHostApiAccessInfo(**self.host_api_access)

        self.host, self.host_owner, self.repo_name = get_repository_info(self.path)

        if not self.platform:
            if "gitlab" in self.host.lower():
                self.platform = "gitlab"
                if self.host_api_access and self.host_api_access.api_base_url == DEFAULT_API_URL:
                    self.host_api_access.api_base_url = f"https://{self.host}/api/v4"
            else:
                self.platform = "github"  # non-breaking change: keep the previous default value

    def ignore_branch(self, branch):
        for calm_branch_regexp in self.calm_branches:
            if re.match(calm_branch_regexp, branch):
                return True
        return False

    def get_branch_url(self, branch):
        return f"https://{self.host}/{self.host_owner}/{self.repo_name}/tree/{branch}"


@dataclasses.dataclass
class BranchInfo:
    repo: str
    name: str
    url: str
    author: str
    age: int
    is_old: bool
    pull_request: githost.PullRequestInfo = None

    @property
    def name_and_details(self):
        details = f"{self.name} ({self.url})"
        if self.pull_request:
            pr = self.pull_request
            details += f", linked to {pr.state} PR/MR #{pr.number} ({pr.url})"
        return details


def get_repository_info(path):
    """Extract the repository owner and name from the origin remote."""
    # Compared to "git config --get remote.origin.url" or "git remote get-url origin", this handles aliases defined in
    # git config.
    remote_url = commands.get_output(("git", "ls-remote", "--get-url"), cwd=path)[0]
    # It usually looks like "git@github.com:Polyconseil/check-oldies.git"
    # but could also look like "poly:check-fixmes.git" if you have an
    # "[url]" section with "insteadOf" in your Git configuration.
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
    parsed = urllib.parse.urlparse(remote_url)
    if parsed.scheme in ('http', 'https', 'ssh'):
        path = parsed.path.lstrip('/')
        host_owner, repo_name = path.split('/', 1)
        # Drop "git@" prefix with ssh scheme
        host = parsed.netloc.split('@')[-1] if parsed.scheme == "ssh" else parsed.netloc
        return host, host_owner, repo_name
    ssh_match = SSH_GIT_URL.match(remote_url)
    if ssh_match:
        path = ssh_match.group('path')
        host_owner, repo_name = path.split('/', 1)
        return ssh_match.group('host'), host_owner, repo_name
    raise ValueError(f"Could not parse remote origin and determine the Git host: '{remote_url}'")


def get_branches(config: Config):
    branches = []
    for branch in commands.get_output(("git", "branch", "--remotes"), cwd=config.path):
        branch = branch.strip()
        if not branch.startswith("origin/"):
            continue
        branch = branch.strip()[len("origin/") :]
        if config.ignore_branch(branch) or "->" in branch:
            continue
        output = commands.get_output(
            ("git", "log", f"origin/{branch}", "-1", "--format=%ae %ci"),
            cwd=config.path,
        )[0]
        # line looks like "john.smith@mail.test 2018-12-19 14:18:52 +0100"
        email, date, *_rest = output.split(" ")
        date = datetime.date(*[int(s) for s in date.split("-")])
        age = (TODAY - date).days
        branches.append(
            BranchInfo(
                repo=config.repo_name,
                name=branch,
                url=config.get_branch_url(branch=branch),
                author=email,
                age=age,
                is_old=age > config.max_age,
            )
        )

    if not branches:
        return ()

    if config.host_api_access:
        pr_getter = githost.PullRequestGetter(config.platform, config.host_owner, config.host_api_access)
        for branch in branches:
            branch.pull_request = pr_getter.get_pull_request(config.repo_name, branch.name)

    return [
        branch
        for branch in branches
        if not config.ignore_branches_without_pull_request or branch.pull_request
    ]
