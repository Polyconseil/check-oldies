import csv
import enum
import io
import os
import typing
import xml.etree.ElementTree

from . import compat


class OutputFormat(compat.StrEnum):
    CSV = enum.auto()
    TEXT = enum.auto()
    XUNIT = enum.auto()


def text_formatter(
    objects: list,
    ok_message: str,
    error_message: str,
    colorize_errors=True,
    **unsupported_options,
) -> str:
    if colorize_errors:
        warn = "\033[91m{}\033[0m".format
    else:
        warn = lambda text: text  # pylint: disable=unnecessary-lambda-assignment

    lines = []
    if ok_message:
        lines.append(ok_message)
    if error_message:
        lines.append(warn(error_message))

    lines.extend(
        warn(obj.to_text()) if obj.must_warn else obj.to_text() for obj in objects
    )

    return os.linesep.join(lines)


def xunit_formatter(
    objects: list,
    error_message: str,
    xunit_suite_name: str,
    xunit_case_name: str,
    xunit_class_name: str,
    **unsupported_options,
) -> str:
    stdout = os.linesep.join(obj.to_text() for obj in objects)
    suite = xml.etree.ElementTree.Element(
        "testsuite",
        {
            "name": xunit_suite_name,
            "tests": "1",
            "errors": "0",
            "failures": "1" if error_message else "0",
        },
    )
    case = xml.etree.ElementTree.SubElement(
        suite,
        "testcase",
        {"classname": xunit_class_name, "name": xunit_case_name},
    )
    if error_message:
        failure = xml.etree.ElementTree.SubElement(
            case,
            "failure",
            {"message": error_message},
        )
        failure.text = stdout

    system_out = xml.etree.ElementTree.SubElement(case, "system-out")
    system_out.text = stdout

    # FIXME (dbaty, 2024-03-28): this element is always empty and
    # could be removed (because the schema says it's optional).
    system_err = xml.etree.ElementTree.SubElement(case, "system-err")
    system_err.text = ""

    return xml.etree.ElementTree.tostring(suite, encoding="utf-8").decode("utf-8")


def _csv_values_converter(values: dict) -> dict:
    converted = {}
    for key, value in values.items():
        csv_value = value
        if csv_value is None:
            csv_value = ""
        elif isinstance(csv_value, bool):
            csv_value = "1" if csv_value else "0"
        converted[key] = csv_value
    return converted


def csv_formatter(objects: list, **unsupported_options) -> str:
    if not objects:
        return ""
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=objects[0].to_dict().keys())
    writer.writeheader()
    for obj in objects:
        writer.writerow(_csv_values_converter(obj.to_dict()))
    return out.getvalue()


def get_formatter(output_format) -> typing.Callable:
    if output_format == OutputFormat.CSV:
        return csv_formatter
    if output_format == OutputFormat.TEXT:
        return text_formatter
    if output_format == OutputFormat.XUNIT:
        return xunit_formatter
    raise ValueError(f"Unknown output format: '{output_format}'")


def printer(objects: list, output_format: OutputFormat, **options):
    formatter = get_formatter(output_format)
    formatted = formatter(objects, **options)
    if formatted:
        print(formatted)
