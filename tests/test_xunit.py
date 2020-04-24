import sys

import pytest

from check_oldies import xunit


# `xml.etree.ElementTree.write()` preserves attribute order only as of
# Python 3.8. With prior versions, we cannot easily compare XML
# output, so don't bother.
HAS_UNSORTED_XML_WRITE = sys.version_info[:2] < (3, 8)


@pytest.mark.skipif(HAS_UNSORTED_XML_WRITE, reason='')
def test_xunit_success(tmp_path):  # tmp_path is a pytest fixture
    path = tmp_path / "subdir" / "xunit.xml"
    xunit.create_xunit_file(
        path,
        suite_name="suite name",
        case_name="case name",
        class_name="class name",
        err_msg="",
        stdout="This is stdout",
        stderr="",
    )
    xml = path.read_text()
    expected = (
        '<testsuite name="suite name" tests="1" errors="0" failures="0">'
        '<testcase classname="class name" name="case name">'
        "<system-out>This is stdout</system-out>"
        "<system-err />"
        "</testcase>"
        "</testsuite>"
    )
    assert xml == expected


@pytest.mark.skipif(HAS_UNSORTED_XML_WRITE, reason='')
def test_xunit_failure(tmp_path):  # tmp_path is a pytest fixture
    path = tmp_path / "subdir" / "xunit.xml"
    xunit.create_xunit_file(
        path,
        suite_name="suite name",
        case_name="case name",
        class_name="class name",
        err_msg="There are errors.",
        stdout="This is stdout",
        stderr="This is stderr",
    )
    xml = path.read_text()
    expected = (
        '<testsuite name="suite name" tests="1" errors="0" failures="1">'
        '<testcase classname="class name" name="case name">'
        '<failure message="There are errors." />'
        "<system-out>This is stdout</system-out>"
        "<system-err>This is stderr</system-err>"
        "</testcase>"
        "</testsuite>"
    )
    assert xml == expected
