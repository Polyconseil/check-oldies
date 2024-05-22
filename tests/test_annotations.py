import datetime
from unittest import mock

from check_oldies import annotations

from . import base


FAKE_GIT_BLAME_OUTPUT = """c106813f91ff43b8fc6e231c263bdaa344866157 136 136 1
some value
some-other value
committer John Smith
committer-mail {mail}
committer-time {timestamp}
committer-tz {offset}
yet-another value
and-a-final value
"""


class TestGetLineBlame:

    # Return a function that mimics what `commands.get_output()`
    # returns for `git blame`.
    def mock_git_blame(self, mail, timestamp, offset):
        def mocked_func(cmd_list, cwd):
            assert " ".join(cmd_list) == "git blame -L 12,12 --porcelain -- file.py"
            assert cwd == "dir"
            output = FAKE_GIT_BLAME_OUTPUT.format(
                mail=mail, timestamp=timestamp, offset=offset
            )
            return output.split("\n")

        return mocked_func

    # Timestamps come from commits of a real Git repository to avoid
    # miscalculations in tests.
    def test_basics(self):
        # Commit eef3c8d8ba059e0f5b77a786bf81511438599eb7 of github.com/pypa/warehouse/
        timestamp = 1466179874  # 2016-06-17 17:11:14
        git_blame = self.mock_git_blame("john@example.com", timestamp, "+0100")
        dt = datetime.datetime(2016, 6, 17, 16, 11, 14, tzinfo=datetime.timezone.utc)
        with mock.patch("check_oldies.commands.get_output", git_blame):
            commit_mail, commit_datetime = annotations.get_line_blame(
                "file.py", "12", cwd="dir"
            )
        assert commit_mail == "john@example.com"
        assert commit_datetime == dt

    def test_timezone_before_utc(self):
        # Commit 382a15fa5e7a0f73e4234dac347cc8d0fe39c41a of github.com/pypa/warehouse/
        timestamp = 1467382795  # 2016-06-17 10:19:55
        git_blame = self.mock_git_blame("john@example.com", timestamp, "-0400")
        dt = datetime.datetime(2016, 7, 1, 14, 19, 55, tzinfo=datetime.timezone.utc)
        with mock.patch("check_oldies.commands.get_output", git_blame):
            commit_mail, commit_datetime = annotations.get_line_blame(
                "file.py", "12", cwd="dir"
            )
        assert commit_mail == "john@example.com"
        assert commit_datetime.astimezone(datetime.timezone.utc) == dt


def test_get_login_from_committer_email():
    login = annotations.get_login_from_committer_email("<john.smith@example.com>")
    assert login == "john.smith"
    login = annotations.get_login_from_committer_email("<@example.com>")
    assert login == "<@example.com>"  # should not be the empty string
    login = annotations.get_login_from_committer_email("John Smith")
    assert login == "John Smith"



class TestGetKnownFutureTag:
    test_data_path = base.TEST_DIR_PATH / "data/project7"

    def test_basics(self):
        tags = annotations.get_known_future_tags(
            directory=self.test_data_path,
            annotation_regex=base.TESTING_ANNOTATIONS[0],
            future_tag_regex=base.TESTING_FUTURE_TAG,
            whitelist=(),
        )
        assert tags == {"FEWTURE-BOOM1", "FEWTURE-BOOM2"}

    def test_whitelist(self):
        tags = annotations.get_known_future_tags(
            directory=self.test_data_path,
            annotation_regex=base.TESTING_ANNOTATIONS[0],
            future_tag_regex=base.TESTING_FUTURE_TAG,
            whitelist=["file2.py"],
        )
        assert tags == {"FEWTURE-BOOM1"}
