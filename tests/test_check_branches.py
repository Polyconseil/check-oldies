"""Integration tests for the ``check-branches`` command."""

import contextlib
import datetime
import os
from unittest import mock

import pytest

from check_oldies import branches
from check_oldies import check_branches
from check_oldies import commands
from check_oldies import output

from . import base


@contextlib.contextmanager
def intercept_commands(replacements):
    orig = commands.get_output

    def mocked(cmd_list, *args, **kwargs):
        try:
            return replacements[" ".join(cmd_list)]
        except KeyError:  # no replacement
            pass
        return orig(cmd_list, *args, **kwargs)

    with mock.patch("check_oldies.commands.get_output", mocked):
        yield


def test_get_repository_info():
    valid_urls = [
        'https://github.com/TestOrg/project_name',
        'https://github.com/TestOrg/project_name.git',
        'ssh://git@github.com/TestOrg/project_name',
        'git@github.com:TestOrg/project_name',
        'git@github.com:TestOrg/project_name.git',
    ]

    for url in valid_urls:
        with mock.patch('check_oldies.commands.get_output', return_value=[url]):
            host, owner, repo_name = branches.get_repository_info('.')
        assert host == 'github.com', url
        assert owner == 'TestOrg', url
        assert repo_name == 'project_name', url

    # Unsupported format
    with mock.patch('check_oldies.commands.get_output', return_value=['ftp://github.com/TestOrg/project_name']):
        with pytest.raises(ValueError):
            host, owner, repo_name = branches.get_repository_info('.')


def test_output_fresh_branches(capfd: pytest.CaptureFixture):
    config = branches.Config(
        path=base.TEST_DIR_PATH.parent,
        max_age=9999,
        colorize_errors=False,
    )

    with mock.patch("check_oldies.configuration.get_config", return_value=config):
        with pytest.raises(SystemExit) as caught_exit:
            check_branches.main()
    captured = capfd.readouterr()

    assert caught_exit.value.code == 0
    stdout = captured.out.rstrip().split(os.linesep)
    # Just check the first line. The next lines may list branches and
    # we would like not to have to mock the output of `git` in this
    # test. We'll do enough ugly things in other tests below...
    assert stdout[0] == "OK: All branches are fresh."


def test_output_old_branches(capfd: pytest.CaptureFixture):
    with pytest.raises(TypeError):
        config = branches.Config(host_owner='Polyconseil')  # pylint: disable=unexpected-keyword-arg

    config = branches.Config(
        path=base.TEST_DIR_PATH.parent,
        colorize_errors=False,
    )

    today = datetime.date.today()
    long_ago = today - datetime.timedelta(days=100)
    replacements = {
        "git branch --remotes": (
            # Yep, extra leading space.
            " origin/master",
            " origin/jsmith/fresh",
            " origin/jsmith/old",
        ),
        "git log origin/jsmith/fresh -1 --format=%ae %ci": (
            f"john.smith@example.com {today.strftime('%Y-%m-%d')} 12:00:00 +0200",
        ),
        "git log origin/jsmith/old -1 --format=%ae %ci": (
            f"john.smith@example.com {long_ago.strftime('%Y-%m-%d')} 12:00:00 +0200",
        ),
    }
    with intercept_commands(replacements):
        with mock.patch("check_oldies.configuration.get_config", return_value=config):
            with pytest.raises(SystemExit) as caught_exit:
                check_branches.main()
    captured = capfd.readouterr()

    assert caught_exit.value.code == 65
    stdout = captured.out.rstrip().split(os.linesep)
    # pylint: disable=line-too-long
    expected = [
        "NOK: Some branches are too old.",
        "john.smith@example.com         -  100 days - jsmith/old (https://github.com/Polyconseil/check-oldies/tree/jsmith/old)",
        "john.smith@example.com         -    0 days - jsmith/fresh (https://github.com/Polyconseil/check-oldies/tree/jsmith/fresh)",
    ]
    assert stdout == expected


def test_xunit_file_generation(capfd: pytest.CaptureFixture):
    config = branches.Config(
        path=base.TEST_DIR_PATH.parent,
        max_age=9999,
        output_format=output.OutputFormat.XUNIT,
    )

    with mock.patch("check_oldies.configuration.get_config", return_value=config):
        with pytest.raises(SystemExit) as caught_exit:
            check_branches.main()
    captured = capfd.readouterr()

    assert caught_exit.value.code == 0
    assert 'failures="0"' in captured.out
