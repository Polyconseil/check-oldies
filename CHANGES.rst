0.8.9 (unreleased)
------------------

- Nothing changed yet.


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
