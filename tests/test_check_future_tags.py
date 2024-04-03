"""Integration tests for the ``check-future-tags`` command."""

import os
from unittest import mock

import pytest

from check_oldies import annotations
from check_oldies import check_future_tags

from . import base


@mock.patch("check_oldies.annotations.get_line_blame", base.fake_get_line_blame)
def test_output_with_orphan_future_tags(capfd):  # capfd is a pytest fixture
    config = annotations.Config(
        path=base.TEST_DIR_PATH / "data/project3",
        colorize_errors=False,
        annotations=base.TESTING_ANNOTATIONS,
        future_tag_regex=base.TESTING_FUTURE_TAG,
    )

    with mock.patch("check_oldies.configuration.get_config", return_value=config):
        with pytest.raises(SystemExit) as caught_exit:
            check_future_tags.main()
    captured = capfd.readouterr()

    assert caught_exit.value.code == 65
    stdout = captured.out.rstrip().split(os.linesep)
    expected = [
        "NOK: There are orphan FUTURE tags.",
        "jane.doe        -   ORPHAN  - file2.py:2: Unknown tag FEWTURE-I-AM-AN-ORPHAN",
    ]
    assert stdout == expected


@mock.patch("check_oldies.annotations.get_line_blame", base.fake_get_line_blame)
def test_output_with_ignored_annotations_orphans_future_tags(capfd):  # capfd is a pytest fixture
    config = annotations.Config(
        path=base.TEST_DIR_PATH / "data/project6",
        colorize_errors=False,
        annotations=base.TESTING_ANNOTATIONS,
        ignored_orphans_annotations=base.TESTING_IGNORED_ORPHANS_ANNOTATIONS,
        future_tag_regex=base.TESTING_FUTURE_TAG,
    )

    with mock.patch("check_oldies.configuration.get_config", return_value=config):
        with pytest.raises(SystemExit) as caught_exit:
            check_future_tags.main()
    captured = capfd.readouterr()

    assert caught_exit.value.code == 65
    stdout = captured.out.rstrip().split(os.linesep)
    expected = [
        'NOK: There are orphan FUTURE tags.',
        'jane.doe        -   ORPHAN  - file2.py:3: Unknown tag FEWTURE-I-AM-AN-ORPHAN'
    ]
    assert stdout == expected
