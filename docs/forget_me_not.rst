=============
forget-me-not
=============


Rationale
=========

**check-branches**, **check-fixmes** and **check-future-tags** can be
run as part of the test suite of each project (by a continuous
integration system such as Jenkins). They break builds when they
detect old annotations or branches.

But nobody wants to see builds break unexpectedly. What if you were
warned that a build *will soon* break because of an old annotation or
an old branch? This is what **forget-me-not** does. Configured with a
warning delay (that defaults to 15 days), it sends an e-mail report to
each author of a soon-to-be breaking old annotation or branch. While
**forget-me-not** could be run on a single project, it makes sense to
run it once accross a set of projects.


Usage and possible customization
================================

.. code-block:: console

    $ forget-me-not --help
    usage: forget-me-not [-h] [--conf CONF] [--warning-delay WARNING_DELAY] [--output {mail,stdout}] [path]

    Warn about annotations and branches that will soo be too old.

    positional arguments:
      path                  Directory that contains all Git repositories to check. Defaults to the working directory.

    optional arguments:
      -h, --help            show this help message and exit
      --conf CONF           Path of the configuration file. Defaults to forget-me-not.toml if it exists.
      --warning-delay WARNING_DELAY
                            Number of days. Annotations and branches are reported if they turn old within this delay. Defaults to 15.
      --output {mail,stdout}


See the :ref:`forget_me_not_configuration` section below for full
details.

To detect old annotations and branches, **forget-me-not** uses the
configuration files **of each project** (or defaults for project that
do not have configuration files). See previous chapters for further
details about the configuration of **check-branches**,
**check-fixmes** and **check-future-tags**.


.. _forget_me_not_configuration:

Configuration
=============

**forget-me-not** takes its own configuration from a TOML file which,
by default and if present, is ``forget-me-not.toml`` in the requested
path (which itself is the current working directory if not provided).
A limited list of options can be overridden via command line arguments
(that you can list with ``forget-me-not --help``). Such overrides take
precedence over the values defined in the configuration files (or the
default values if omitted).

The TOML configuration file should not have any top-level sections.
Here is an example:


.. code-block:: toml

    warning-delay = 15
    ignored-repositories = [
        'systools',
    ]

    # SMTP
    smtp.host = "localhost"

    # Recipients
    recipients.catch-all = "developers@example.com"
    recipients.list = [
        "john.smith@example.com",
        "jane.doe@example.com",
    ]
    [recipients.aliases]
    johnny = "john.smith@example.com"


Here is the list of all options that can be configured via the TOML
configuration file:

.. contents::
   :local:
   :depth: 2


General options
---------------

``ignored-repositories``
........................

A list of repositories not to check.

| Type: list.
| Default: ``[]`` (no repository is ignored).
| Example: ``ignored-repositories = ["legacy-project"]``.


``output`` (overridable via the command line)
.............................................

Whether **forget-me-not** should print reports on the standard output,
send reports by e-mail, or both.

| Type: list.
| Default: ``["stdout"]`` (do not send e-mail reports by default).
| Example: ``["stdout", "mail"]``.

On the command-line, you can provide multiple values by using the
option twice:

.. code-block:: console

    $ forget-me-not --output stdout --output mail


``path`` (overridable via the command line)
...........................................

The path of the directory in which **forget-me-not** looks for Git
repositories to check. It must be a directory.

| Type: string.
| Default: ``"."`` (current working directory).
| Example: ``path = "/path/to/all/checkouts"``.


``warning-delay`` (overridable via the command line)
....................................................

The number of days to warn before an annotation or a branch is
considered old, as per the configuration of each project.

| Type: integer.
| Default: ``15`` (days).
| Example: ``warning-delay = 7``.



E-mail-related options
----------------------

The text of the e-mail can be configured with multiple options. Here
is how it is built::

    {email-body-intro}
    {email-body-annotations}
    {email-body-branches}
    {email-body-outro}

With the default values, that gives:

.. code-block:: text

        Hello,

    You have {count} old annotation(s) that will block builds
    in less than {warning_delay} days:

    {lines}

    You have {count} old branch(es) that will block builds
    in less than {warning_delay} days:

    {lines}

     -- 
     Sent by forget-me-not

Each annotation is reported using the ``email-body-annotation-line-template``.
By default, it looks like this::

    {age} days: {repo}:{path}:{line_no}: {line_content}

Each branch is reported using the ``email-body-branch-line-template``.
By default, it looks like this::

    {age} days: {repo}: {branch_details}


``email_sender``
................

| Type: string.
| Default: ``"forget-me-not@example.com"``
| Example: ``email-sender = "no-reply@example.com"``.



``email_subject``
.................

| Type: string.
| Default: ``"W{week_number}: Old annotations and old branches"``
| Example: ``email-subject = "forget-me-not report for week {week_number}"``.

The ``{week_number}`` part will be automatically replaced.


``smtp``
........

This option is a table in TOML parlance, also known as dictionary,
mapping, hash table, etc.

It looks like this:

.. code-block:: toml

    smtp.host = "smtp.example.com"
    smtp.port = 12345

See below for the possible keys in this table.


``smtp.host``
.............

The SMTP host to use to send e-mail reports.

| Type: string.
| Default: ``"localhost"`` (do not send e-mail reports by default).
| Example: ``smtp.host = "smtp.example.com"``.


``smtp.port``
.............

The port to use when contacting the SMTP host to send e-mail reports.

| Type: integer.
| Default: ``0`` (uses OS default behaviour).
| Example: ``smtp.port = 12345``.

``smtp.user``
.............

The user to use when contacting the SMTP host to send e-mail reports.

| Type: string.
| Example: ``smtp.user = "USERNAME"``.

``smtp.password``
.................

The password to use when contacting the SMTP host to send e-mail reports.

| Type: string.
| Example: ``smtp.password = "SECRET"``.
