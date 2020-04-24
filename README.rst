**check-oldies** is a collection of programs that warn about old
things in code:

- **check-fixmes** warns about old FIXME or TODO annotations and
  orphan FUTURE tags.

  If we did not regularly check, we would forget about that FIXME note
  we wrote a few months ago. **check-fixmes** warns us about it. It is
  then our choice to act: fix it, remove it (because we decided it is
  not worth to fix, or because it is not relevant anymore), or
  postpone it.

  FUTURE tags: We sometimes plan a broad modification that will span
  multiple files. Instead of littering FIXME annotations everywhere,
  we set a single FIXME annotation and a FUTURE-xxx tag on the same
  line. Then, wherever we need to make a modification, we only
  mention this FUTURE-xxx tag without any FIXME. If we ever remove the
  FIXME but keep a FUTURE-xxx tag somewhere, it is a mistake and this
  tool warns us.

- **check-branches** warns about old branches, surprisingly.

- **forget-me-not** runs both programs above on a set of Git
  repositories and sends warning e-mails to authors of soon-to-be-old
  annotations or branches.

In other words: **check-fixmes** and **check-branches** can be run as
part of the test suite of each project (by a continuous integration
system such as Jenkins). They break builds when they detect old
things.  On the other hand, **forget-me-not** can be run once a week
on a set of projects to warn authors that some builds *will* break
soon if they do not take care of their old annotations or branches.


Example output
==============

::

    $ check-fixmes
    NOK: Some annotations are too old, or there are orphan FUTURE tags.
    jdoe            -  181 days - frobulator/api.py:12: # FIXME (jdoe): we should catch errors
    jdoe            -  100 days - frobulator/api.py:25: # TODO: this is slow, use the batch API instead
    jsmith          -   12 days - docs/index.rst:1: # FIXME: write documentation before open sourcing


::

    $ check-branches
    NOK: Some branches are too old.
    john.smith@example.com     -   92 days - jsmith/fix_frobs (https://github.com/Polyconseil/check-oldies/tree/jsmith/fix_frobs), linked to open PR/MR #1 (https://github.com/Polyconseil/check-oldies/pull/1)


Applicability
=============

**check-oldies** is written in Python but is language-agnostic. It
works on Git repositories but could be extended to other version
control systems. It integrates with GitHub but can do without it, and
could be extended to work with other code hosting platforms.


Requirements and installation
=============================

You must have Python 3.6 or later, and a relatively recent version of
Git. Git 2.1.4 (shipped with Debian Jessie) is known to work. More
recent versions should work and are supported.

Install with ``pip``, preferably in a virtual environment:

.. code-block:: console

    $ python3 -m venv /path/to/your/virtualenv
    $ source /path/to/your/virtualenv/bin/activate

    $ pip install "check-oldies[toml]"


Features, configuration and more
================================

The `full documentation`_ has more details about the features and the
configuration, examples of the usage of FUTURE tags, how to
contribute, etc.

.. _full documentation: https://check-oldies.readthedocs.io/
