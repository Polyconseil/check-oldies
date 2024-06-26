1.0.0 (unreleased)
------------------

- |backward-incompatible| Remove ``--xunit-file`` argument from all
  commands. It can be replaced by a new ``--format=xunit`` argument
  and redirecting the standard output to a file, like this::

      $ check-fixmes --format=xunit > xunit.xml

  This change is needed to properly introduce the ``--format``
  argument that controls the formatting output, which is now directed
  to the standard output.

- |backward-incompatible| A new **check-future-tags** command is
  introduced that reports orphan future tags. **check-fixmes** does
  **not** report those tags anymore, it only reports outdated FIXME's.

- All commands now have a CSV output format, available with the
  ``--format=csv`` argument.

- **check-fixmes** and **check-branches** commands now have a
  ``--only-old`` argument to show, well, only old annotations or
  branches.


0.8.10 (2023-08-16)
-------------------

- Add main branch to calm branches


0.8.9 (2023-03-13)
------------------

- Adapt xunit syntax for gitlab reports


0.8.8 (2023-01-11)
------------------

- Add SMTP authentication
- |backward-incompatible| Drop support of Python 3.6.


0.8.7 (2021-11-15)
------------------

- Add support for ssh URL with protocol (e.g. ssh://git@github.com/TestOrg/project_name)


0.8.6 (2021-10-18)
------------------

- Add Gitlab support.


0.8.5 (2021-10-08)
------------------

- Add ``ignore_orphans_annotations`` config option.
  This option ignore orphan future tags check on ignored annotations.


0.8.4 (2020-11-18)
------------------

- Automatically detect the appropriate ``host_owner`` if undefined, in
  ``check-branches``.
- |backward-incompatible| **check-branches**: Drop ``host_owner`` option in the configuration file. You should remove
  this option, otherwise an error will occur while reading the configuration file.


0.8.3 (2020-10-27)
------------------

- Generate a wheel. For real. Or so I hope...


0.8.2 (2020-10-27)
------------------

- Fix generation of wheel on release. Only a tarball was released, now
  a wheel should be released as well.

- Fix compatibility with git < 2.7 in ``check-branches``.


0.8.1 (2020-10-26)
------------------

- Fix xUnit output that contained control characters when
  ``check-fixmes`` or ``check-branches`` were not run with the
  ``--no-color`` option.


0.8.0 (2020-10-22)
------------------

First public release.


0.1.0 (2016-01-12)
------------------

First apparition in a private tool.


.. role:: raw-html(raw)
.. |backward-incompatible| raw:: html

    <span style="background-color: #ffffbc; padding: 0.3em; font-weight: bold;">backward incompatible</span>
