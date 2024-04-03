"""Integration tests for the ``check-fixmes`` command."""

import os
from unittest import mock

import pytest

from check_oldies import annotations
from check_oldies import check_fixmes

from . import base


@mock.patch("check_oldies.annotations.get_line_blame", base.fake_get_line_blame)
def test_output_when_all_annotations_are_fresh(capfd):  # capfd is a pytest fixture
    config = annotations.Config(
        path=base.TEST_DIR_PATH / "data/project1",
        max_age=9999,
        colorize_errors=False,
        annotations=base.TESTING_ANNOTATIONS,
        future_tag_regex=base.TESTING_FUTURE_TAG,
    )

    with mock.patch("check_oldies.configuration.get_config", return_value=config):
        with pytest.raises(SystemExit) as caught_exit:
            check_fixmes.main()
    captured = capfd.readouterr()

    assert caught_exit.value.code == 0
    stdout = captured.out.rstrip().split(os.linesep)
    expected = [
        "OK: All annotations are fresh.",
        "jane.doe        -    2 days - file1.py:1: # TIMEBOMB: report me",
        "jane.doe        -    2 days - file1.py:8: # TIMEBOMB - FEWTURE-BOOM: report me",
        "jane.doe        -    2 days - file2.py:1: # TIMEBOMB: report me",
        "jsmith          -    2 days - file1.py:2: a = 1  # TIMEBOMB (jsmith): report me",
        "jsmith          -    2 days - file1.py:4: # TIMEBOMB(jsmith - 2020-04-25): report me",
    ]
    assert stdout == expected


def test_output_when_no_annotations(capfd):  # capfd is a pytest fixture
    config = annotations.Config(path=base.TEST_DIR_PATH / "data/project2")

    with mock.patch("check_oldies.configuration.get_config", return_value=config):
        with pytest.raises(SystemExit) as caught_exit:
            check_fixmes.main()
    captured = capfd.readouterr()

    assert caught_exit.value.code == 0
    stdout = captured.out.rstrip().split(os.linesep)
    expected = [
        "OK: No annotations were found.",
    ]
    assert stdout == expected



def test_xunit_file_generation(tmp_path):  # tmp_path is a pytest fixture
    xunit_path = tmp_path / "xunit.xml"
    config = annotations.Config(
        path=base.TEST_DIR_PATH / "data/project2",
        xunit_file=xunit_path,
    )

    with mock.patch("check_oldies.configuration.get_config", return_value=config):
        with pytest.raises(SystemExit) as caught_exit:
            check_fixmes.main()

    assert caught_exit.value.code == 0
    assert 'failures="0"' in xunit_path.read_text()
