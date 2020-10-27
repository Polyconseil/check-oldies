import dataclasses
import datetime
import os
import pathlib
import re
import typing

from . import commands
from . import githost


TODAY = datetime.date.today()


@dataclasses.dataclass
class GitHostApiAccessInfo:
    platform: str = "github"
    api_base_url: str = "https://api.github.com"
    auth_token_file: str = None
    auth_token_env_var: str = None

    def __post_init__(self):
        self.auth_token = self.get_auth_token()

    def get_auth_token(self):
        if self.auth_token_file:
            return pathlib.Path(self.auth_token_file).expanduser().read_text().strip()
        if self.auth_token_env_var:
            return os.environ[self.auth_token_env_var]
        raise ValueError(
            "Missing configuration to get authentication token for Git host API."
        )


@dataclasses.dataclass
class Config:
    path: str = "."
    max_age: int = 90

    colorize_errors: bool = True
    xunit_file: str = None

    calm_branches: typing.Sequence = ("gh-pages", "master", "prod", "maint(enance)?/.*")
    ignore_branches_without_pull_request: bool = False

    host_owner: str = None
    host_url: str = "https://github.com/{owner}/{repo}/tree/{branch}"
    host_api_access: dict = None

    def __post_init__(self):
        if self.host_api_access:
            self.host_api_access = GitHostApiAccessInfo(**self.host_api_access)

    def ignore_branch(self, branch):
        for calm_branch_regexp in self.calm_branches:
            if re.match(calm_branch_regexp, branch):
                return True
        return False


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


def get_repository_name(path):
    """Extract the repository name from the origin remote."""
    # When we can use git >= 2.7, we'll be able to use `git remote get-url origin`.
    url = commands.get_output(("git", "config", "--get", "remote.origin.url"), cwd=path)[0]
    # It usually looks like "git@github.com:Polyconseil/check-oldies.git"
    # but could also look like "poly:check-fixmes.git" if you have an
    # "[url]" section with "insteadOf" in your Git configuration.
    if url.endswith(".git"):
        url = url[:-4]
    return url.rsplit("/", 1)[-1].rsplit(":", 1)[-1]


def get_branches(config: Config):
    repo = get_repository_name(config.path)

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
        url = config.host_url.format(owner=config.host_owner, repo=repo, branch=branch)
        branches.append(
            BranchInfo(
                repo=repo,
                name=branch,
                url=url,
                author=email,
                age=age,
                is_old=age > config.max_age,
            )
        )

    if not branches:
        return ()

    if config.host_api_access:
        pr_getter = githost.PullRequestGetter(config.host_owner, config.host_api_access)
        for branch in branches:
            branch.pull_request = pr_getter.get_pull_request(repo, branch.name)

    return [
        branch
        for branch in branches
        if not config.ignore_branches_without_pull_request or branch.pull_request
    ]
