import datetime
import os
import pathlib


TEST_DIR_PATH = pathlib.Path(os.path.dirname(__file__))
# We don't want to whitelist test files because we may want to add
# real annotations in tests (that we want to be picked up by
# check-fixmes). For this we need custom annotations and tags in
# tests.
TESTING_ANNOTATIONS = ["TIMEBOMB"]
TESTING_FUTURE_TAG = r"FEWTURE-[-[:alnum:]\._]+?"


# We need to force the age of each line (i.e. the datetime of the
# latest commit that touched each line) that we want to display,
# otherwise we would not be able to control the output. With more work
# we could perhaps mock only the output of `git blame`, but
# `get_line_blame` is appropriately tested already. So we'll settle on
# less work.
def fake_get_line_blame(filename, line, cwd):
    committer_email = "<jane.doe@example.com>"
    commit_datetime = datetime.datetime.now() - datetime.timedelta(days=2)
    return committer_email, commit_datetime.astimezone(datetime.timezone.utc)
