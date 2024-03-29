=================
check-future-tags
=================

Features and usage
==================

This command detects orphan "FUTURE" tags.


Rationale and principles
------------------------

Developers sometimes plan broad modifications that will span multiple
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
``file2.py``, it is a mistake and **check-future-tags** warns us.


Usage and possible customization
--------------------------------

**check-future-tags** looks for tags that start with ``FUTURE-``
(e.g. ``FUTURE-SWITCH-TO-V2``) to make sure that at least one of them
appears on the same line as an annotation. If not, it is considered an
orphan tag and is reported as an error.

As for annotations, you can ignore a line by using
``no-check-fixmes``, and ignore whole files with the :ref:`whitelist
option <check_future_tags_conf_whitelist>`. You can configure how tags are detected with
the :ref:`future_tag_regex option <check_future_tags_conf_future_tag_regex>`.

See the :ref:`check_future_tags_configuration` section below for full details.


.. _check_future_tags_configuration:

Configuration
=============

**check-future-tags** takes its configuration from a TOML file. By
default and if present, ``pyproject.toml`` is read (as a courtesy for
Python projects, even though **check-future-tags** is
language-agnostic). A limited list of options can be overridden via
command line arguments (that you can list with ``check-future-tags
--help``). Such overrides take precedence over the values defined in
the configuration files (or the default values if omitted).

The TOML configuration file should have a ``[tool.check-future-tags]``
section, like this:

.. code-block:: toml

    [tool.check-future-tags]
    path = "src"
    max-age = 30

For an example configuration file, see `the configuration file
<https://github.com/Polyconseil/check-oldies/blob/master/pyproject.toml#L1-L14>`_
of the **check-future-tags** project itself.

Here is the list of all options that can be configured via the TOML
configuration file:

.. contents::
   :local:
   :depth: 2


Input options
-------------

.. _check_future_tags_conf_path:

``path`` (overridable via the command line)
...........................................

The path of the directory in which **check-future-tags** looks for
annotations (recursively). It must be a Git checkout repository.

| Type: string.
| Default: ``"."`` (current working directory).
| Example: ``path = "src"``.


.. _check_future_tags_conf_whitelist:

``whitelist``
.............

If the ``no-check-fixmes`` pragma is not appropriate, you may
whitelist whole files by providing a list of glob patterns.

| Type: list.
| Default: ``[]`` (no whitelist).
| Example: ``whitelist = ["docs/*"]``.


Output options
--------------

.. _check_future_tags_conf_colorize_errors:

``colorize-errors``
...................

By default, errors (old annotations and orphan FUTURE tags) appear
in red. Set this option to ``false`` if you want to use the
default foreground color.

| Type: boolean.
| Default: ``true``.
| Example: ``colorize-errors = false``.


.. _check_future_tags_conf_format:

``format`` (overridable via the command line)
.............................................

The output format.

| Type: string, one of: ``csv``, ``text`` or ``xunit``.
| Default: ``text``
| Example: ``format = "xunit"``.


Detection options
-----------------

.. _check_future_tags_conf_annotations:

``annotations``
...............

The list of annotations to look for. Note that **check-future-tags** is
case insensitive: by default, both "todo", "TODO", "fixme" and
"FIXME" will be reported.

| Type: list.
| Default: ``["fixme", "todo"]`` (case insensitive).
| Example: ``annotations = ["todo", "optimize", "fixme", "hack"]``.


.. _check_future_tags_conf_future_tag_regex:

``future-tag-regex``
....................

The extended regular expression to use to detect FUTURE tags.

| Type: string (an extended regular expression).
| Default: ``"FUTURE-[-[:alnum:]\._]+?"``.
| Example: ``future-tag-regex = "HEREAFTER-[-[:alnum:]\._]+?"``.

.. _check_future_tags_conf_ignored_orphans_annotations:

``ignored_orphans_annotations``
...............................

The list of annotations which will not trigger orphan FUTURE tags
checks.  Note that **check-future-tags** is case insensitive: by
default, both "wontfix", "WONTFIX" will be ignored.

| Type: list.
| Default: ``["wontfix", "xxx"]`` (case insensitive).
| Example: ``ignored_orphans_annotations = ["wontfix", "nofix"]``.
