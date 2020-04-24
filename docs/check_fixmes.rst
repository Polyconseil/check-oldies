============
check-fixmes
============

Features and usage
==================

There are two main features:

- detection of old annotations (FIXME, TODO, etc.);
- detection of forgotten FUTURE tags.


Detection of old annotations
----------------------------

Rationale and principles
........................

Developers use annotations to indicate that some code is deficient:
FIXME, TODO, OPTIMIZE, HACK, BUG, etc. Semantics vary, but the overall
meaning is the same: the annotated code should be changed, some day.
Sometimes very soon, sometimes hypothetically.

Time passes and these annotations tend to be forgotten or ignored.

**check-fixmes** warns about annotations that it considers too old. It
is then the developer's choice to act: remove the annotation (because
we decided it is not worth to fix, or because it is not relevant
anymore), change the code, or postpone the annotation.

The only way to postpone an annotation is to commit a change on its
line. To simplify that, a good habit is to indicate today's date
beside the annotation. The date can then be quickly updated without
changing the rest of the line (nor its length) when we decide to
postpone.  Example:

.. code-block:: text

    FIXME (2020-01-04): I am getting heartburn. Tony, do something terrible.

Note that this date is not taken in account by **check-fixmes** to
calculate the age of the annotation. We found that it was not useful
and possibly error-prone. Instead, the date of the last commit is
used.


Usage and possible customization
................................

.. code-block:: console

    $ check-fixmes --help
    usage: check-fixmes [-h] [--conf CONF] [--max-age MAX_AGE] [--no-color] [--xunit-file XUNIT_FILE] [path]

    Check your code for unattended annotations

    positional arguments:
      path                  Git-managed path where search should happen. Defaults to the working directory.

    optional arguments:
      -h, --help            show this help message and exit
      --conf CONF           Path of the configuration file. Defaults to pyproject.toml if it exists.
      --max-age MAX_AGE     Maximum age in days allowed for an annotation, errors otherwise. Defaults to 180.
      --no-color            Do not colorize errors. Defaults to colorizing errors in red.
      --xunit-file XUNIT_FILE
                            Path of the xUnit report file to write. Defaults to no xUnit output.


The age of the annotation is calculated from the time of the last
commit that touched the line the annotation appears on.

The author of each annotation is reported, again by looking at the
last commit that touched the line. You may also assign someone else
by formatting your annotation like this:

.. code-block:: text

    FIXME (jsmith): It is up to John to do something here.

As suggested above, you can indicate a date to more easily postpone
the FIXME. The default format looks like this:

.. code-block:: text

    FIXME (jsmith, 2020-04-01): It is up to John to do something here.

You can mark a line as not to be reported with the string
``no-check-fixmes``. This is useful if you are using a word that would
be an annotation, but not in this context. For example, in a CSS file:

.. code-block:: css

    div {
      background: url('img/todo.png'); /* no-check-fixmes */
    }

If you need to ignore whole files, see the :ref:`whitelist option
<conf_whitelist>`.

Possible customizations:

- which type of annotations are taken in account (FIXME, TODO,
  OPTIMIZE, etc.): see the :ref:`annotations option
  <conf_annotations>`;

- how assignments are formatted: see the the :ref:`assignee_regex
  option <conf_assignee_regex>`;

- the age above which an annotation is considered old: see the
  :ref:`max-age option <conf_max_age>`;

See the :ref:`check_fixmes_configuration` section below for full details.


Detection of orphan FUTURE tags
-------------------------------

Rationale and principles
........................

Developers sometimes plan a broad modification that will span multiple
files. Instead of littering FIXME annotations everywhere, they can set
a single FIXME annotation and a FUTURE-xxx tag on the same line. Then,
wherever we need to make a modification, we only mention this
FUTURE-xxx tag without any FIXME. If we have to "postpone" a FIXME,
there is only line to touch.

Example:

.. code-block:: text

    # in file1.py:
    #
    #     FIXME (jsmith, FUTURE-SWITCH-TO-V2): remove this field when we switch to v2
    #
    # in file2.py:
    #
    #     FUTURE-SWITCH-TO-V2: deprecate usage when we switch to v2

If we ever remove the FIXME but keep the FUTURE-SWITCH-TO-V2 tag in
``file2.py``, it is a mistake and **check-fixmes** warns us.


Usage and possible customization
................................

**check-fixmes** looks for tags that start with ``FUTURE-``
(e.g. ``FUTURE-SWITCH-TO-V2``) to make sure that at least one of them
appears on the same line as an annotation. If not, it is considered an
orphan tag and is reported as an error.

As for annotations, you can ignore a line by using
``no-check-fixmes``, and ignore whole files with the :ref:`whitelist
option <conf_whitelist>`. You can configure how tags are detected with
the :ref:`future_tag_regex option <conf_future_tag_regex>`.

See the :ref:`check_fixmes_configuration` section below for full details.


.. _check_fixmes_configuration:

Configuration
=============

**check-fixmes** takes its configuration from a TOML file. By default
and if present, ``pyproject.toml`` is read (as a courtesy for Python
projects, even though **check-fixmes** is language-agnostic). A
limited list of options can be overridden via command line arguments
(that you can list with ``check-fixmes --help``). Such overrides take
precedence over the values defined in the configuration files (or the
default values if omitted).

The TOML configuration file should have a ``[tool.check-fixmes]``
section, like this:

.. code-block:: toml

    [tool.check-fixmes]
    path = "src"
    max-age = 30

For an example configuration file, see `the configuration file
<https://github.com/Polyconseil/check-oldies/blob/master/pyproject.toml#L1-L14>`_
of the **check-oldies** project itself.

Here is the list of all options that can be configured via the TOML
configuration file:

.. contents::
   :local:
   :depth: 2


Input options
-------------

.. _conf_path:

``path`` (overridable via the command line)
...........................................

The path of the directory in which **check-fixmes** looks for
annotations (recursively). It must be a Git checkout repository.

| Type: string.
| Default: ``"."`` (current working directory).
| Example: ``path = "src"``.


.. _conf_whitelist:

``whitelist``
.............

If the ``no-check-fixmes`` pragma is not appropriate, you may
whitelist whole files by providing a list of glob patterns.

| Type: list.
| Default: ``[]`` (no whitelist).
| Example: ``whitelist = ["docs/*"]``.


Output options
--------------

.. _conf_colorize_errors:

``colorize-errors``
...................

By default, errors (old annotations and orphan FUTURE tags) appear
in red. Set this option to ``false`` if you want to use the
default foreground color.

| Type: boolean.
| Default: ``true``.
| Example: ``colorize-errors = false``.


.. _conf_xunit_file:

``xunit-file`` (overridable via the command line)
.................................................

The path to the xUnit report file to generate. **check-fixmes**
gracefully creates parent directories of the file if they do not
exist.

| Type: string (a path).
| Default: none (no xUnit file is generated).
| Example: ``xunit-file = "reports/xunit.xml"``.


Detection options
-----------------

.. _conf_annotations:

``annotations``
...............

The list of annotations to look for. Note that **check-fixmes** is
case insensitive: by default, both "todo", "TODO", "fixme" and
"FIXME" will be reported.

| Type: list.
| Default: ``["fixme", "todo"]`` (case insensitive).
| Example: ``annotations = ["todo", "optimize", "fixme", "hack"]``.


.. _conf_assignee_regex:

``assignee-regex``
..................

The regular expression (using `Python syntax`_) to use to extract the
assignee in an annotation. Requirements:

- it should contain the string ``{annotation_regex}``.
  **check-fixmes** will replace it by the proper regex that match
  all annotations;

- it must have a group named ``assignee``.

| Type: string (a Python regular expression).
| Default: ``"(?:{annotation_regex})\s*\((?P<assignee>\w+)"`` (matches ``FIXME (jsmith)``).
| Example: ``assignee-regex = "(?:{annotation_regex})\s*- (?P<assignee>\w+)"`` (matches ``FIXME - jsmith``).

.. _Python syntax: https://docs.python.org/3/library/re.html#regular-expression-syntax


.. _conf_future_tag_regex:

``future-tag-regex``
....................

The extended regular expression to use to detect FUTURE tags.

| Type: string (an extended regular expression).
| Default: ``"FUTURE-[-[:alnum:]\._]+?"``.
| Example: ``future-tag-regex = "HEREAFTER-[-[:alnum:]\._]+?"``.


.. _conf_max_age:

``max-age`` (overridable via the command line)
..............................................

The age (in days) above which an annotation is considered old.

| Type: integer.
| Default: ``180``.
| Example: ``max-age = 30``.
