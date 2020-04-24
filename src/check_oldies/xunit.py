import os
from xml.etree import ElementTree


def create_xunit_file(
    output_path,
    suite_name,
    case_name,
    class_name,
    err_msg,
    stdout,
    stderr,
):
    """Create an xUnit file.

    If the parent directory of ``output_path`` does not exist, it is
    transparently created.
    """
    suite = ElementTree.Element(
        "testsuite",
        {
            "name": suite_name,
            "tests": "1",
            "errors": "0",
            "failures": "1" if err_msg else "0",
        },
    )

    case = ElementTree.SubElement(
        suite, "testcase", {"classname": class_name, "name": case_name}
    )
    if err_msg:
        ElementTree.SubElement(case, "failure", {"message": err_msg})
    system_out = ElementTree.SubElement(case, "system-out")
    system_out.text = stdout

    system_err = ElementTree.SubElement(case, "system-err")
    system_err.text = stderr

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ElementTree.ElementTree(suite).write(output_path, encoding="utf-8")
