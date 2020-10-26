import argparse
import os
import sys

from . import branches
from . import configuration
from . import xunit


def get_parser():
    parser = argparse.ArgumentParser(
        prog="check-branches", description="Check your code for unattended branches"
    )
    parser.add_argument(
        "--conf",
        help=(
            f"Path of the configuration file. "
            f"Defaults to {configuration.PYPROJECT_FILENAME} if it exists."
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        help=(
            "Git-managed path where search should happen. "
            "Defaults to the working directory."
        ),
    )
    parser.add_argument(
        "--max-age",
        type=int,
        help=(
            f"Maximum age in days allowed for a branch, errors otherwise. "
            f"Defaults to {branches.Config.max_age}."
        ),
    )
    parser.add_argument(
        "--no-color",
        action="store_false",
        default=True,
        dest="colorize_errors",
        help="Do not colorize errors. Defaults to colorizing errors in red.",
    )
    parser.add_argument(
        "--xunit-file",
        action="store",
        help="Path of the xUnit report file to write. Defaults to no xUnit output.",
    )
    return parser


def branch_str(branch):
    return (
        f"{branch.author[:30]: <30} - {branch.age: >4} days - {branch.name_and_details}"
    )


def main():
    parser = get_parser()
    config = configuration.get_config(
        "check-branches", parser, sys.argv[1:], branches.Config
    )
    if not configuration.is_git_directory(config.path):
        sys.exit(f'Invalid path: "{config.path}" is not a Git repository.')

    if config.colorize_errors:
        warn = "\033[91m{}\033[0m".format
    else:
        warn = lambda text: text

    all_branches = branches.get_branches(config)

    out = []
    uncolorized_out = []
    for branch in sorted(
        all_branches, key=lambda branch: (branch.author, -branch.age, branch.name)
    ):
        line = branch_str(branch)
        out.append(warn(line) if branch.is_old else line)
        uncolorized_out.append(line if branch.is_old else line)
    has_old_branches = any(branch for branch in all_branches if branch.is_old)

    out = os.linesep.join(out)
    if has_old_branches:
        err_msg = "NOK: Some branches are too old."
        print(err_msg)
    else:
        err_msg = ""
        print("OK: All branches are fresh.")
    if out:
        print(out)

    if config.xunit_file:
        uncolorized_out = os.linesep.join(uncolorized_out)
        xunit.create_xunit_file(
            os.path.abspath(config.xunit_file),
            "check-branches",
            "branches",
            "CheckBranches",
            err_msg=err_msg,
            stdout=uncolorized_out,
            stderr="",
        )

    sys.exit(os.EX_DATAERR if has_old_branches else os.EX_OK)


if __name__ == "__main__":  # pragma: no cover
    main()
