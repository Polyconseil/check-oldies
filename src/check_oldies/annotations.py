import collections
import dataclasses
import datetime
import re
import subprocess
import typing

import pkg_resources

from . import commands
from . import output


IGNORE_PRAGMA = "no-check-fixmes"


# All default values are here (not in the `config` module) to be close
# to the code that uses them.
@dataclasses.dataclass
class Config:
    path: str = "."
    max_age: int = 180

    output_format: output.OutputFormat = output.OutputFormat.TEXT
    only_old: bool = False
    colorize_errors: bool = True

    annotations: typing.Sequence = ("todo", "fixme", )  # no-check-fixmes
    ignored_orphans_annotations: typing.Sequence = ("wontfix", "xxx")  # annotation which won't trigger orphans checks
    assignee_regex: str = r"(?:{annotation_regex})\s*\((?P<assignee>[\w\._-]+)"
    future_tag_regex: str = r"FUTURE-[-[:alnum:]\._]+?"  # no-check-fixmes

    whitelist: typing.Sequence = ()

    @property
    def annotation_regex(self):
        return "|".join(self.annotations).lower()

    @property
    def ignored_orphans_annotations_regex(self):
        return "|".join(self.ignored_orphans_annotations).lower()

    @property
    def _annotation_with_boundaries_regex(self):
        annotation_regex = r'\b|\b'.join(self.annotations).lower()
        return fr'\b{annotation_regex}\b'

    @property
    def py_annotation_regex(self):
        """Python compiled regex to extract an annotation."""
        # pylint: disable=access-member-before-definition
        if hasattr(self, "_py_annotation_regex"):
            return self._py_annotation_regex
        # Only accept tags if preceded by #, <, {, some space, /, * or line start
        self._py_annotation_regex = re.compile(
            fr"((?<=#|\s|/|\*|<|{{)|^)({self._annotation_with_boundaries_regex})",
            re.IGNORECASE | re.UNICODE,
        )
        return self._py_annotation_regex

    @property
    def py_assignee_regex(self):
        """Python compiled regex to extract the assignee."""
        # pylint: disable=access-member-before-definition
        if hasattr(self, "_py_assignee_regex"):
            return self._py_assignee_regex
        # Should look like "FIXME (jsmith)", the space is optional. [no-check-fixmes]
        self._py_assignee_regex = re.compile(
            self.assignee_regex.format(annotation_regex=self.annotation_regex),
            re.IGNORECASE | re.UNICODE,
        )
        return self._py_assignee_regex


@dataclasses.dataclass
class Annotation:
    path: str
    line_no: int
    line_content: str
    age: int = None
    assignee: str = None
    is_old: bool = None

    @property
    def must_warn(self):
        return self.is_old

    def to_text(self):
        return (
            f"{self.assignee: <15} - {self.age: >4} days - "
            f"{self.path}:{self.line_no}: {self.line_content.strip()}"
        )

    def to_dict(self):
        return {
            "path": self.path,
            "line_no": self.line_no,
            "assignee": self.assignee,
            "line_content": self.line_content,
            "age": self.age,
            "is_old": self.is_old,
        }


@dataclasses.dataclass
class FutureTag:
    path: str
    line_no: int
    tag: str
    author: str = None

    must_warn = True

    def to_text(self):
        return (
            f"{self.author: <15} -   ORPHAN  - "
            f"{self.path}:{self.line_no}: Unknown tag {self.tag}"
        )

    def to_dict(self):
        return {
            "path": self.path,
            "line_no": self.line_no,
            "tag": self.tag,
            "author": self.author,
        }


def get_annotation_candidates(directory, annotation_regex, whitelist):
    """Return lines (with filename and line number) that contains an annotation."""
    return commands.get_output(
        [
            "git",
            "grep",
            "-I",  # Ignore binary files
            "--line-number",
            "--ignore-case",
            "--extended-regexp",
            "-e",  # Find annotations
            annotation_regex,
            "--and",  # When they do not contain the ignore pragma ("no-check-fixmes")
            "--not",
            "-e",
            IGNORE_PRAGMA,
            "--",
            ".",
        ]
        + [f":(exclude){glob}" for glob in whitelist],
        cwd=directory,
        valid_return_codes=(0, 1),  # 1 means that no files were found
    )


def get_line_blame(filename, line, cwd):
    """Return author's email and timestamp of the latest commit that
    touched this line.
    """
    infos = commands.get_output(
        ["git", "blame", f"-L {line},{line}", "--porcelain", "--", filename],
        cwd=cwd,
    )

    def _get_info(metadata):
        return [info.split()[1] for info in infos if info.startswith(metadata)][0]

    committer_mail = _get_info("committer-mail")
    timestamp = int(_get_info("committer-time"))
    timezone = _get_info("committer-tz")
    multiplier = 1 if timezone[0] == "+" else -1
    hours = int(timezone[1:3])
    minutes = int(timezone[3:5])
    tz = datetime.timezone(
        multiplier * datetime.timedelta(hours=hours, minutes=minutes)
    )
    commit_datetime = datetime.datetime.fromtimestamp(timestamp).astimezone(tz)
    return committer_mail, commit_datetime


def get_login_from_committer_email(committer_email):
    login_match = re.match(r"<(?P<login>.+)@", committer_email)
    if login_match:
        return login_match.group("login")
    return committer_email


def get_annotations(config: Config):
    annotations = []
    for candidate in get_annotation_candidates(
        config.path, config.annotation_regex, config.whitelist
    ):
        filename, line_no, line_content = candidate.split(":", 2)
        # FIXME (dbaty, 2024-03-28): it should be possible to apply
        # the right regex (with boundaries) directly in git grep.
        if config.py_annotation_regex.search(line_content):
            annotations.append(Annotation(filename, int(line_no), line_content))

    for annotation in annotations:
        last_committer, last_modification = get_line_blame(
            annotation.path, annotation.line_no, cwd=config.path
        )
        last_committer = get_login_from_committer_email(last_committer)
        match = config.py_assignee_regex.search(annotation.line_content)
        annotation.assignee = match.group("assignee") if match else last_committer
        annotation.age = (
            datetime.datetime.now(datetime.timezone.utc) - last_modification
        ).days
        annotation.is_old = annotation.age > config.max_age
    return annotations


def get_known_future_tags(directory, annotation_regex, future_tag_regex, whitelist):
    """Return a list of tags that are referenced along annotations."""
    grep = [
        "git",
        "grep",
        "-I",  # ignore binary files
        "--ignore-case",
        "--extended-regexp",
        f"{annotation_regex}.*{future_tag_regex}",
        "--",
        ".",
    ]
    grep.extend([f":(exclude){glob}" for glob in whitelist])
    lines = commands.get_pipe_command_output(
        grep,
        piped_to=f'sed --regexp-extended "s/.*?({future_tag_regex}).*?/\\1/g"',
        cwd=directory,
        valid_return_codes=(0, 1),  # 0 if there are matches, 1 otherwise
    )
    return set(lines)


def git_supports_only_matching():
    out = subprocess.check_output(["git", "--version"]).decode("utf-8")
    # output looks like "git version 2.26.0"
    git_version = pkg_resources.parse_version(out.split()[2])
    # `git grep --only-matching` appeared in Git 2.19.0
    # https://github.com/git/git/blob/v2.19.0/Documentation/RelNotes/2.19.0.txt#L41
    minimal_version = pkg_resources.parse_version("2.19.0")
    return git_version >= minimal_version


def get_all_futures(directory, future_tag_regex, whitelist):
    """Get all occurrences of FUTURE tags."""
    # Old versions of Git (such as Git 2.1.4 that is shipped by Debian
    # Jessie) do not support the `--only-matching` option. Pipe to
    # `sed` instead.
    if git_supports_only_matching():
        grep = [
            "git",
            "grep",
            "-I",  # ignore binary files
            "--line-number",
            "--extended-regexp",
            "--only-matching",
            "-e",
            future_tag_regex,
            "--and",
            "--not",
            "-e",
            IGNORE_PRAGMA,
        ]
        grep.extend([f":(exclude){glob}" for glob in whitelist])
        lines = commands.get_output(
            grep,
            cwd=directory,
            valid_return_codes=(0, 1),  # 0 if there are matches, 1 otherwise
        )
    else:
        grep = [
            "git",
            "grep",
            "-I",  # ignore binary files
            "--line-number",
            "--extended-regexp",
            "-e",
            future_tag_regex,
            "--and",
            "--not",
            "-e",
            IGNORE_PRAGMA,
            "--",  # needed on old versions...
            ".",  # ... of git
        ]
        grep.extend([f":(exclude){glob}" for glob in whitelist])
        sed = f'sed --regexp-extended "s/(.*?):.*?({future_tag_regex}).*?/\\1:\\2/g"'
        lines = commands.get_pipe_command_output(
            grep,
            piped_to=sed,
            cwd=directory,
            valid_return_codes=(0, 1),  # 0 if there are matches, 1 otherwise
        )

    occurrences = collections.defaultdict(list)
    for line in lines:
        path, line_no, tag = line.split(":", 2)
        occurrences[tag].append(FutureTag(path=path, line_no=int(line_no), tag=tag))
    return occurrences


def get_orphan_futures(config):
    """Return orphan FUTURE tags.

    A FUTURE tag is orphan if it does not also appear (elsewhere) on a
    line with an annotation.
    """
    known_tags = get_known_future_tags(
        config.path,
        fr'{config.ignored_orphans_annotations_regex}|{config.annotation_regex}',
        config.future_tag_regex, config.whitelist,
    )
    futures = get_all_futures(config.path, config.future_tag_regex, config.whitelist)
    orphans = []
    for tag, occurrences in sorted(futures.items()):
        if tag in known_tags:
            continue
        occurrences = sorted(occurrences, key=lambda occ: (occ.path, occ.line_no))
        for occurrence in occurrences:
            last_committer_email, _last_modification = get_line_blame(
                occurrence.path, occurrence.line_no, cwd=config.path
            )
            occurrence.author = get_login_from_committer_email(last_committer_email)
            orphans.append(occurrence)
    return orphans
