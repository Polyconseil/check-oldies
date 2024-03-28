import argparse

import pytest

from check_oldies import annotations
from check_oldies import configuration
from check_oldies import output

from . import base


@pytest.fixture
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--conf")
    parser.add_argument("--max-age", type=int)
    return parser


# pylint: disable=redefined-outer-name
def test_get_config_from_config_file(arg_parser):
    argv = [str(base.TEST_DIR_PATH)]
    config = configuration.get_config(
        "check-fixmes", arg_parser, argv, annotations.Config
    )
    assert config.path == str(base.TEST_DIR_PATH)
    assert config.max_age == 180
    assert config.colorize_errors
    assert config.output_format == output.OutputFormat.TEXT
    assert config.annotations == ["fixme", "todo"]


def test_get_config_override_from_command_line(arg_parser):
    argv = [str(base.TEST_DIR_PATH), "--max-age", "1"]
    config = configuration.get_config(
        "check-fixmes", arg_parser, argv, annotations.Config
    )
    assert config.max_age == 1


def test_is_git_repository(tmp_path):  # tmp_path is a pytest fixture
    assert configuration.is_git_directory(base.TEST_DIR_PATH)
    assert not configuration.is_git_directory(tmp_path)
