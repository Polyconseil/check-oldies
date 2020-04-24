"""Integration tests for the ``forget-me-not`` command."""

import contextlib
import os
from unittest import mock

from check_oldies import forget_me_not

from . import base


@contextlib.contextmanager
def in_working_directory(path):
    current = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(current)


@mock.patch("check_oldies.annotations.get_line_blame", base.fake_get_line_blame)
def test_forget_me_not(capfd):  # capfd is a pytest fixture
    with in_working_directory(base.TEST_DIR_PATH / 'data'):
        forget_me_not.main(argv=[])
    captured = capfd.readouterr()

    stdout = captured.out.rstrip().split(os.linesep)
    expected = [
        "Found annotations or old branches of unknown authors (forwarded to catch-all@example.com):",
        "jane.doe",
        "unknown",
        "catch-all@example.com",
        "    Hello,",
        "",
        "You have 2 old annotation(s) that will block builds in less than 15 days:",
        "",
        "2 days: project5:file1.py:1: # TIMEBOMB: report me (no author => catch-all)",
        "2 days: project5:file1.py:2: # TIMEBOMB (unknown): report me (unknown author => catch-all)",
        "",
        "-- ",
        "Sent by forget-me-not",
        "",
        "--------------------",
        "john.smith@example.com",
        "    Hello,",
        "",
        "You have 3 old annotation(s) that will block builds in less than 15 days:",
        "",
        "2 days: project5:file1.py:3: # TIMEBOMB (jsmith): report me to john.smith@example.com",
        "2 days: project5:file1.py:4: # TIMEBOMB (js): report me to john.smith@example.com (alias)",
        "2 days: project5:file1.py:5: # TIMEBOMB (john.smith@example.com): report me to john.smith@example.com (email)",
        "",
        "-- ",
        "Sent by forget-me-not",
        "",
        "--------------------",
    ]
    assert stdout == expected
