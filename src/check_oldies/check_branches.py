import argparse
import os
import sys

import check_oldies.branches

from . import configuration
from . import output


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
        "--format",
        default=output.OutputFormat.TEXT,
        dest="output_format",
        help="Output format. Defaults to human-readable text (one result per line).",
        choices=sorted(output.OutputFormat),
        type=output.OutputFormat,
    )
    parser.add_argument(
        "--max-age",
        type=int,
        help=(
            f"Maximum age in days allowed for a branch, errors otherwise. "
            f"Defaults to {check_oldies.branches.Config.max_age}."
        ),
    )
    parser.add_argument(
        "--only-old",
        action="store_true",
        default=False,
        help="Show only old branches. By default, the command shows all branches."
    )
    parser.add_argument(
        "--no-color",
        action="store_false",
        default=True,
        dest="colorize_errors",
        help="Do not colorize errors. Defaults to colorizing errors in red.",
    )
    return parser


def main():
    parser = get_parser()
    config = configuration.get_config(
        "check-branches", parser, sys.argv[1:], check_oldies.branches.Config
    )
    if not configuration.is_git_directory(config.path):
        sys.exit(f'Invalid path: "{config.path}" is not a Git repository.')

    branches = check_oldies.branches.get_branches(config)
    if config.only_old:
        branches = [branch for branch in branches if branch.is_old]
    branches.sort(key=lambda branch: (branch.author, -branch.age, branch.name))
    has_old_branches = any(branch for branch in branches if branch.is_old)

    ok_msg = err_msg = ""
    if has_old_branches:
        err_msg = "NOK: Some branches are too old."
    else:
        ok_msg = "OK: All branches are fresh."

    output.printer(
        branches,
        config.output_format,
        ok_message=ok_msg,
        error_message=err_msg,
        colorize_errors=config.colorize_errors,
        xunit_suite_name="check-branches",
        xunit_case_name="branches",
        xunit_class_name="CheckBranches",
    )

    sys.exit(os.EX_DATAERR if has_old_branches else os.EX_OK)


if __name__ == "__main__":  # pragma: no cover
    main()
