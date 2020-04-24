import subprocess

import pytest

from check_oldies import commands

from . import base


class TestGetCommandOutput:
    def test_success(self):
        lines = commands.get_output(
            ["head", "-n 4", "test_commands.py"], cwd=base.TEST_DIR_PATH,
        )
        # Yes, we'll need to change it every time we change an import.
        # We'll survive.
        expected = [
            "import subprocess",
            "import pytest",
        ]
        assert lines == expected

    def test_unexpected_return_code(self):
        with pytest.raises(subprocess.CalledProcessError):
            commands.get_output(
                ["head", "-n 4", "test_commands.py"],
                valid_return_codes=[1234],
                cwd=base.TEST_DIR_PATH,
            )


def test_get_pipe_command_output():
    lines = commands.get_pipe_command_output(
        ["head", "-n 4", "test_commands.py"],
        piped_to="head -n 1",
        cwd=base.TEST_DIR_PATH,
    )
    expected = [
        "import subprocess",
    ]
    assert lines == expected
