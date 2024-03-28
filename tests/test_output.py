import sys

import pytest

from check_oldies import output


# `xml.etree.ElementTree.tostring()` preserves attribute order only as of
# Python 3.8. With prior versions, we cannot easily compare XML
# output, so don't bother.
HAS_UNSORTED_XML_WRITE = sys.version_info[:2] < (3, 8)


class FakeResult:
    def __init__(self, var):
        self.var = var

    def to_text(self):
        return f"fake: {self.var}"


@pytest.mark.skipif(HAS_UNSORTED_XML_WRITE, reason="")
def test_xunit_formatter_success():
    results = [FakeResult(1), FakeResult(2)]
    xml = output.xunit_formatter(
        results,
        error_message="",
        xunit_suite_name="suite name",
        xunit_case_name="case name",
        xunit_class_name="class name",
    )
    assert xml == (
        '<testsuite name="suite name" tests="1" errors="0" failures="0">'
        '<testcase classname="class name" name="case name">'
        "<system-out>fake: 1\nfake: 2</system-out>"
        "<system-err />"
        "</testcase>"
        "</testsuite>"
    )


@pytest.mark.skipif(HAS_UNSORTED_XML_WRITE, reason="")
def test_xunit_formatter_failure():
    results = [FakeResult(1), FakeResult(2)]
    xml = output.xunit_formatter(
        results,
        error_message="A dramatic error occurred!",
        xunit_suite_name="suite name",
        xunit_case_name="case name",
        xunit_class_name="class name",
    )
    assert xml == (
        '<testsuite name="suite name" tests="1" errors="0" failures="1">'
        '<testcase classname="class name" name="case name">'
        '<failure message="A dramatic error occurred!">fake: 1\nfake: 2</failure>'
        "<system-out>fake: 1\nfake: 2</system-out>"
        "<system-err />"
        "</testcase>"
        "</testsuite>"
    )
