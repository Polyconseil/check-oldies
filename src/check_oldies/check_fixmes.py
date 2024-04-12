import argparse
import os
import sys

import check_oldies.annotations

from . import configuration
from . import output


def get_parser():
    parser = argparse.ArgumentParser(
        prog="check-fixmes", description="Check your code for unattended annotations"
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
            f"Maximum age in days allowed for an annotation, errors otherwise. "
            f"Defaults to {check_oldies.annotations.Config.max_age}."
        ),
    )
    parser.add_argument(
        "--only-old",
        action="store_true",
        default=False,
        help="Show only old annotations. By default, the command shows all annotations."
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
        "check-fixmes", parser, sys.argv[1:], check_oldies.annotations.Config
    )
    if not configuration.is_git_directory(config.path):
        sys.exit(f'Invalid path: "{config.path}" is not a Git repository.')

    annotations = check_oldies.annotations.get_annotations(config)
    if config.only_old:
        annotations = [a for a in annotations if a.is_old]
    annotations.sort(key=lambda f: (f.assignee, -f.age, f.filename, f.line_no))
    has_old_annotations = any(ann for ann in annotations if ann.is_old)

    ok_msg = err_msg = ""
    if has_old_annotations:
        err_msg = "NOK: Some annotations are too old."
    else:
        if annotations:
            ok_msg = "OK: All annotations are fresh."
        else:
            ok_msg = "OK: No annotations were found."

    output.printer(
        annotations,
        config.output_format,
        ok_message=ok_msg,
        error_message=err_msg,
        colorize_errors=config.colorize_errors,
        xunit_suite_name="check-fixmes",
        xunit_case_name="fixmes",
        xunit_class_name="CheckFixmes",
    )

    sys.exit(os.EX_DATAERR if has_old_annotations else os.EX_OK)


if __name__ == "__main__":  # pragma: no cover
    main()
