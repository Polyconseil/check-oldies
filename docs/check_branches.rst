==============
check-branches
==============

Features and usage
==================

Rationale and principle
-----------------------

When developers work on multiple projects, or have multiple tasks on
the same project, it is not rare to forget about one of them. Branches
can rot with time and become harder to merge.

**check-branches** warns about branches that it considers too old. It
is then the developer's choice to act: refresh it or delete it.

The age of a branch is computed from the date of its latest commit.
The author of a branch is reported by looking at the author of the
latest commit.


Usage
-----

.. code-block:: console

    $ check-branches --help
    usage: check-branches [-h] [--conf CONF] [--format {csv,text,xunit}] [--max-age MAX_AGE] [--no-color] [path]

    Check your code for unattended branches

    positional arguments:
      path                  Git-managed path where search should happen. Defaults to the working directory.

    options:
      -h, --help            show this help message and exit
      --conf CONF           Path of the configuration file. Defaults to pyproject.toml if it exists.
      --format {csv,text,xunit}
                            Output format. Defaults to human-readable text (one result per line).
      --max-age MAX_AGE     Maximum age in days allowed for a branch, errors otherwise. Defaults to 90.
      --no-color            Do not colorize errors. Defaults to colorizing errors in red.


Tip
---

When you cannot do anything better, you can quickly make a branch
fresh by pushing an empty commit (that you can squash later):

.. code-block:: console

    $ git ci --allow-empty --fixup=@ -m "empty commit to make check-branches happy"


.. _check_branches_configuration:

Configuration
=============

**check-branches** takes its configuration from a TOML file. By
default and if present, ``pyproject.toml`` is read (as a courtesy for
Python projects, even though **check-branches** is language-agnostic).
A limited list of options can be overridden via command line arguments
(that you can list with ``check-branches --help``). Such overrides
take precedence over the values defined in the configuration files (or
the default values if omitted).

The TOML configuration file should have a ``[tool.check-branches]``
section, like this:

.. code-block:: toml

    [tool.check-branches]
    max-age = 30

For an example configuration file, see `the configuration file
<https://github.com/Polyconseil/check-oldies/blob/master/pyproject.toml#L17-L18>`_
of the **check-oldies** project itself.

Here is the list of all options that can be configured via the TOML
configuration file:

.. contents::
   :local:
   :depth: 2


General options
---------------

``calm-branches``
.................

A list of regular expressions (using `Python syntax`_). Branches that
match one of these regexps will be ignored.

| Type: list.
| Default: ``["gh-pages", "master", "prod", "maint(enance)?/.*"]``.
| Example: ``calm-branches = ["master", "dev"]``.

.. _Python syntax: https://docs.python.org/3/library/re.html#regular-expression-syntax


``ignore-branches-without-pull-request``
........................................

This option only makes sense if you have configured access to a Git
hosting platform, see :ref:`check_branches_host_api_access` below. It
allows to ignore branches for which there is no pull/merge request.
This is mostly useful for forks or projects where you keep a lot of
long-running branches for which the ``calm_branches`` option is not
adequate.

| Type: boolean.
| Default: ``false`` (i.e. report a branch as old whether there is a
  related pull/merge request or not).
| Example: ``ignore_branches_without_pull_request = true``.


``max-age`` (overridable via the command line)
..............................................

The age (in days) above which a branch is considered old.

| Type: integer.
| Default: ``90``.
| Example: ``max-age = 30``.


``path`` (overridable via the command line)
...........................................

The path of the directory in which **check-branches** looks for
branches. It must be a Git checkout repository.

| Type: string.
| Default: ``"."`` (current working directory).
| Example: ``path = "/path/to/git/checkout"``.


Git hosting platform
--------------------

These options relate to GitHub, GitLab and other hosting platforms
where your project may reside. They are used to provide links to web
pages that show the branch and the associated pull/merge request, if
any.

Currently, only GitHub is supported. It should not be too hard to
extend to other platforms. :doc:`Contributions are welcome.<contributing>`.


.. _check_branches_host_api_access:

``host-api-access``
...................

This option is a table in TOML parlance, also known as dictionary,
mapping, hash table, etc.

It looks like this:

.. code-block:: toml

    host-api-access.platform = 'github'
    host-api-access.auth-token-file = '~/.config/github_auth_token'

See below for the possible keys in this table. Currently, only GitHub
and Gitlab are supported.

If your repository is hosted on GitHub or Gitlab, you only need to
configure one of the authentication token-related options. The
default value of the other options are tailored for GitHub.

If you do *not* have access to the API of a Git hosting platform,
don't configure anything in ``host-api-access``.


``host-api-access.api-base-url``
...................................

The base URL of the web API of the Git hosting platform.

| Type: string.
| Default: ``"https://api.github.com"``.
| Example: ``host-api-access.api-base-url = "https://gitlab.com/api/v4"``.


``host-api-access.auth-token-env-var``
......................................

The name of the environment variable that contains the authentication
token to access the web API of the Git hosting platform.

| Type: string.
| Default: ``None``.
| Example: ``host-api-access.auth-token-env-var = "GITHUB_AUTH_TOKEN"``.

An authentication token must be set with this option or
``auth-token-file`` (see below).


``host-api-access.auth-token-file``
...................................

The path to the file that contains the authentication token to access
the web API of the Git hosting platform.

| Type: string.
| Default: ``None``.
| Example: ``host-api-access.auth-token-file = "~/.config/github_auth_token"``.

An authentication token must be set with this option or
``auth-token-env-var`` (see above).


``host-api-access.platform``
............................

The name of the Git hosting platform. This is used to determine the
API client to use. For now, only ``github`` and ``gitlab`` are
supported.

| Type: string.
| Default: ``"github"``.
| Example: ``host-api-access.platform = "gitlab"``.


``host-url``
............

The pattern to be used to build the URL of each branch of the
repository. The default value is tailored for GitHub. The ``{owner}``
value is extracted from the remote origin's URL.

| Type: string.
| Default: ``"https://github.com/{owner}/{repo}/tree/{branch}"``.
| Example: ``host-url = "https://gitview.example.com/{owner}/{repo}/tree/{branch}"``.


Output options
--------------

``colorize-errors``
...................

By default, errors (old branches) appear in red. Set this option to
``false`` if you want to use the default foreground color.

| Type: boolean.
| Default: ``true``.
| Example: ``colorize-errors = false``.


``format`` (overridable via the command line)
.............................................

The output format.

| Type: string, one of: ``csv``, ``text`` or ``xunit``.
| Default: ``text``
| Example: ``format = "xunit"``.


``only-old`` (overridable via the command line)
...............................................

By default, all branches are displayed. When this option is enabled,
only old branches are displayed.

| Type: boolean.
| Default: ``false``
| Example: ``only-old = true``.
