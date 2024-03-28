import argparse
import os
import sys

from . import annotations
from . import configuration
from . import output


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
        "--format",
        default=output.OutputFormat.TEXT,
        dest="output_format",
        help="Output format. Defaults to human-readable text (one result per line).",
        choices=sorted(output.OutputFormat),
        type=output.OutputFormat,
    )
    return parser


def main():
    parser = get_parser()
    config = configuration.get_config(
        "check-future-tags", parser, sys.argv[1:], annotations.Config
    )
    if not configuration.is_git_directory(config.path):
        sys.exit(f'Invalid path: "{config.path}" is not a Git repository.')

    orphan_futures = annotations.get_orphan_futures(config)

    ok_msg = err_msg = ""
    if orphan_futures:
        err_msg = "NOK: There are orphan FUTURE tags."
    else:
        ok_msg = "OK: No orphan FUTURE tags were found."

    output.printer(
        orphan_futures,
        config.output_format,
        ok_message=ok_msg,
        error_message=err_msg,
        colorize_errors=config.colorize_errors,
        xunit_suite_name="check-future-tags",
        xunit_case_name="future-tags",
        xunit_class_name="CheckFutureTags",
    )

    sys.exit(os.EX_DATAERR if orphan_futures else os.EX_OK)


if __name__ == "__main__":  # pragma: no cover
    main()
