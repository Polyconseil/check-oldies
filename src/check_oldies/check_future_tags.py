import argparse
import os
import sys

from . import annotations
from . import configuration
from . import xunit


def orphan_str(orphan):
    return (
        f"{orphan.author: <15} -   ORPHAN  - "
        f"{orphan.path}:{orphan.line_no}: Unknown tag {orphan.tag}"
    )


def get_parser():
    parser = argparse.ArgumentParser(
        prog="check-future-tags", description="Check your code for unattended future tags"
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


def main():
    parser = get_parser()
    config = configuration.get_config(
        "check-future-tags", parser, sys.argv[1:], annotations.Config
    )
    if not configuration.is_git_directory(config.path):
        sys.exit(f'Invalid path: "{config.path}" is not a Git repository.')

    if config.colorize_errors:
        warn = "\033[91m{}\033[0m".format
    else:
        warn = lambda text: text  # pylint: disable=unnecessary-lambda-assignment

    # Look for orphan FUTURE tags
    out = []
    uncolorized_out = []
    orphan_futures = annotations.get_orphan_futures(config)
    for orphan in orphan_futures:
        out.append(warn(orphan_str(orphan)))
        uncolorized_out.append(orphan_str(orphan))

    out = os.linesep.join(out)
    if orphan_futures:
        err_msg = "NOK: There are orphan FUTURE tags."
        print(err_msg)
    else:
        err_msg = ""
        print("OK: No orphan FUTURE tags were found.")
    if out:
        print(out)

    if config.xunit_file:
        uncolorized_out = os.linesep.join(uncolorized_out)
        xunit.create_xunit_file(
            os.path.abspath(config.xunit_file),
            suite_name="check-future-tags",
            case_name="future-tags",
            class_name="CheckFutureTags",
            err_msg=err_msg,
            stdout=uncolorized_out,
            stderr="",
        )

    sys.exit(os.EX_DATAERR if orphan_futures else os.EX_OK)


if __name__ == "__main__":  # pragma: no cover
    main()
