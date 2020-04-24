import argparse
import collections
import dataclasses
import datetime
from email.message import EmailMessage
import pathlib
import smtplib
import sys
import typing

from . import annotations
from . import branches
from . import configuration


CATCH_ALL = object()
CONFIGURATION_FILE = 'forget-me-not.toml'


@dataclasses.dataclass
class RecipientConfig:
    catch_all: str
    list: typing.Sequence
    aliases: dict = dataclasses.field(default_factory=dict)

    @property
    def email_mapping(self):
        if hasattr(self, '_mapping'):
            return self._mapping  # pylint: disable=access-member-before-definition
        self._mapping = {}
        # john.smith@example.com gets two aliases: "john.smith" and "jsmith".
        for email in self.list:
            fullname = email.split('@')[0]
            self._mapping[fullname] = email
            if '.' in fullname:
                firstname, lastname = fullname.split('.')
                # XXX: duplicate aliases are not handled
                self._mapping[f'{firstname[0]}{lastname}'] = email
        self._mapping.update(self.aliases)
        return self._mapping

    def get_email(self, author):
        if '@' in author:  # assume it's an e-mail address
            return author
        return self.email_mapping.get(author)


@dataclasses.dataclass
class SmtpConfig:
    host: str
    port: int = 0  # use OS default behaviour

    def make_connection(self):
        return smtplib.SMTP(self.host, port=self.port)


@dataclasses.dataclass
class Config:
    recipients: dict
    path: str = '.'
    warning_delay: int = 15
    ignored_repositories: typing.Sequence = ()
    output: typing.Sequence = ("stdout", )

    smtp: dict = dataclasses.field(default_factory=lambda: {'host': 'localhost'})

    email_sender: str = "forget-me-not@example.com"
    email_subject: str = "W{week_number}: Old annotations and old branches"
    email_body_intro: str = "    Hello,\n\n"
    email_body_outro: str = "\n\n-- \nSent by forget-me-not"
    email_body_annotations: str = "\n".join((
        "You have {count} old annotation(s) that will block builds "
        "in less than {warning_delay} days:",
        "",
        "{lines}",
    ))
    email_body_annotation_line_template: str = (
        "{age} days: {repo}:{path}:{line_no}: {line_content}"
    )
    email_body_branches: str = "\n".join((
        "You have {count} old branch(es) that will block builds "
        "in less than {warning_delay} days:",
        "",
        "{lines}",
    ))
    email_body_branch_line_template: str = "{age} days: {repo}: {branch_details}"


    def __post_init__(self):
        assert set(self.output).issubset({"stdout", "mail"})
        self.recipients = RecipientConfig(**self.recipients)
        if self.smtp:
            self.smtp = SmtpConfig(**self.smtp)


@dataclasses.dataclass
class FakeArgumentParser:
    # An object that mimics what we get from ArgumentParser.parse_args().
    path: pathlib.Path
    conf: pathlib.Path

    def parse_args(self, argv):
        return self


def check_repositories(config):
    all_reports = {
        'annotations': [],
        'branches': []
    }
    for path in sorted(pathlib.Path(config.path).iterdir()):
        if not path.is_dir():
            continue
        if path.stem in config.ignored_repositories:
            continue
        if not configuration.is_git_directory(path):
            continue
        repo_reports = check_repository(path, config.warning_delay)
        all_reports["annotations"].extend(repo_reports["annotations"])
        all_reports["branches"].extend(repo_reports["branches"])
    return all_reports


def check_repository(path, warning_delay):
    repo_config_path = path / configuration.PYPROJECT_FILENAME
    if not repo_config_path.exists():
        repo_config_path = None  # we'll use the default config
    ann_config = configuration.get_config(
        tool_name="check-fixmes",
        arg_parser=FakeArgumentParser(path=path, conf=repo_config_path),
        argv=[],
        config_class=annotations.Config,
    )
    branches_config = configuration.get_config(
        tool_name="check-branches",
        arg_parser=FakeArgumentParser(path=path, conf=repo_config_path),
        argv=[],
        config_class=branches.Config,
    )
    ann_config.max_age -= warning_delay
    branches_config.max_age -= warning_delay
    all_annotations = annotations.get_annotations(ann_config)
    for annotation in all_annotations:
        annotation.repository = path.stem
    all_branches = branches.get_branches(branches_config)
    return {
        "annotations": [ann for ann in all_annotations if ann.is_old],
        "branches": [branch for branch in all_branches if branch.is_old],
    }


def group_reports_by_email(reports, config):
    by_email = collections.defaultdict(dict)
    unknown_users = set()

    for report_key, recipient_getter in (
        ("annotations", lambda ann: ann.assignee),
        ("branches", lambda branch: branch.author),
    ):
        for warning in reports[report_key]:
            recipient = recipient_getter(warning)
            email = config.recipients.get_email(recipient)
            if not email:
                unknown_users.add(recipient)
                email = CATCH_ALL
            by_email[email].setdefault(report_key, []).append(warning)

    return by_email, unknown_users


def generate_emails(reports_by_email, config):
    week_number = datetime.date.today().isocalendar()[1]
    email_subject = config.email_subject.format(week_number=week_number)
    for recipient, reports in reports_by_email.items():
        body = config.email_body_intro
        all_annotations = reports.get("annotations")
        if all_annotations:
            # If no user is assigned, promote oldest lines because
            # they are the most urgent to fix. Otherwise, keep the
            # original order (by repository, filename and line number)
            # because it makes more sense to group annotations in each
            # repository.
            if recipient == CATCH_ALL:
                all_annotations.sort(key=lambda ann: ann.age)
            lines = []
            for annotation in all_annotations:
                lines.append(
                    config.email_body_annotation_line_template.format(
                        age=annotation.age,
                        repo=annotation.repository,
                        path=annotation.filename,
                        line_no=annotation.line_no,
                        line_content=annotation.line_content.strip(),
                    )
                )
            body += config.email_body_annotations.format(
                count=len(lines),
                warning_delay=config.warning_delay,
                lines="\n".join(lines)
            )

        all_branches = reports.get("branches")
        if all_branches:
            # Sort as we did for annotations above.
            if recipient == CATCH_ALL:
                all_branches.sort(key=lambda ann: ann.age)
            lines = [
                config.email_body_branch_line_template.format(
                    age=branch.age,
                    repo=branch.repo,
                    branch_details=branch.name_and_details,
                )
                for branch in all_branches
            ]
            if all_annotations:
                body += '\n\n'
            body += config.email_body_branches.format(
                count=len(lines),
                warning_delay=config.warning_delay,
                lines='\n'.join(lines),
            )

        body += config.email_body_outro

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = email_subject
        msg["From"] = config.email_sender
        if recipient == CATCH_ALL:
            msg["To"] = config.recipients.catch_all
        else:
            msg["To"] = recipient
        yield msg


def get_parser():
    parser = argparse.ArgumentParser(
        prog="forget-me-not",
        description="Warn about annotations and branches that will soo be too old."
    )
    parser.add_argument(
        'path',
        nargs='?',
        help=(
            "Directory that contains all Git repositories to check. "
            "Defaults to the working directory."
        ),
    )
    parser.add_argument(
        "--conf",
        help=(
            f"Path of the configuration file. "
            f"Defaults to {CONFIGURATION_FILE} if it exists."
        ),
    )
    parser.add_argument(
        "--warning-delay",
        type=int,
        help=(
            f"Number of days. "
            f"Annotations and branches are reported if they turn old within this delay. "
            f"Defaults to {Config.warning_delay}."
        ),
    )
    parser.add_argument(
        '--output', choices=['mail', 'stdout'], action='append', default=['stdout'],
    )
    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = get_parser()
    config = configuration.get_config(
        None,
        parser,
        argv,
        Config,
        'forget-me-not.toml',
    )

    reports = check_repositories(config)
    reports_by_email, unknown_users = group_reports_by_email(reports, config)
    emails = list(generate_emails(reports_by_email, config))

    if unknown_users:
        catch_all = config.recipients.catch_all
        print(
            f"Found annotations or old branches of unknown authors "
            f"(forwarded to {catch_all}):"
        )
        print('\n'.join(sorted(unknown_users)))

    if "stdout" in config.output:
        for email in emails:
            print(email["To"])
            print(email.get_content())
            print("-" * 20)
    if "mail" in config.output:
        with config.smtp.make_connection() as smtp:
            for email in emails:
                smtp.send_message(email)
                print(f"Sent e-mail to {email['To']}")


if __name__ == "__main__":  # pragma: no cover
    main()
