import argparse
import os
import sys

from . import annotations
from . import configuration
from . import xunit


def annotation_str(annotation):
    return (
        "{assignee: <15} - {age_days: >4} days - "
        "{filename}:{line_no}: {line_content}"
    ).format(
        assignee=annotation.assignee[:15],
        age_days=annotation.age,
        filename=annotation.filename,
        line_no=annotation.line_no,
        line_content=annotation.line_content.strip(),
    )


def orphan_str(orphan):
    return (
        "{author: <15} -   ORPHAN  - "
        "{orphan.path}:{orphan.line_no}: Unknown tag {orphan.tag}"
    ).format(author=orphan.author[:15], orphan=orphan)


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
        "--max-age",
        type=int,
        help=(
            f"Maximum age in days allowed for an annotation, errors otherwise. "
            f"Defaults to {annotations.Config.max_age}."
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
        "check-fixmes", parser, sys.argv[1:], annotations.Config
    )
    if not configuration.is_git_directory(config.path):
        sys.exit(f'Invalid path: "{config.path}" is not a Git repository.')

    if config.colorize_errors:
        warn = "\033[91m{}\033[0m".format
    else:
        warn = lambda text: text

    # Look for old annotations
    out = []
    uncolorized_out = []
    all_annotations = sorted(
        annotations.get_annotations(config),
        key=lambda f: (f.assignee, -f.age, f.filename, f.line_no),
    )
    for annotation in all_annotations:
        line = annotation_str(annotation)
        out.append(warn(line) if annotation.is_old else line)
        uncolorized_out.append(line if annotation.is_old else line)
    has_old_annotations = any(ann for ann in all_annotations if ann.is_old)

    # Look for orphan FUTURE tags
    orphan_futures = annotations.get_orphan_futures(config)
    for orphan in orphan_futures:
        out.append(warn(orphan_str(orphan)))
        uncolorized_out.append(orphan_str(orphan))

    out = os.linesep.join(out)
    if has_old_annotations or orphan_futures:
        err_msg = "NOK: Some annotations are too old, or there are orphan FUTURE tags."
        print(err_msg)
    else:
        err_msg = ""
        if all_annotations:
            print("OK: All annotations are fresh.")
        else:
            print("OK: No annotations were found.")
    if out:
        print(out)

    if config.xunit_file:
        uncolorized_out = os.linesep.join(uncolorized_out)
        xunit.create_xunit_file(
            os.path.abspath(config.xunit_file),
            suite_name="check-fixmes",
            case_name="fixmes",
            class_name="CheckFixmes",
            err_msg=err_msg,
            stdout=uncolorized_out,
            stderr="",
        )

    sys.exit(os.EX_DATAERR if has_old_annotations or orphan_futures else os.EX_OK)


if __name__ == "__main__":  # pragma: no cover
    main()
