Contributing
============

**check-oldies** is open source and contributions are most welcome.
You may propose ideas, report bugs, provide code or documentation.
Typo and grammar fixes are warmly received as well.

You may report a bug or propose a change or a new feature by opening
`an issue on GitHub <https://github.com/Polyconseil/check-oldies/issues>`_.

If you have some time at hand and the inclination to do so, you may
directly open a pull request. It will be very much appreciated. Here
are a few guidelines. Obviously, not everything is relevant if you are
only fixing a typo in the documentation.

.. note::

    tl;dr: run ``make test``, run ``make quality``, create a pull
    request on GitHub that clearly explains what your changes do and
    **why you need it**. Check the status of your branch on GitHub
    Action, be nice and be patient. :)

#. Fork the `Polyconseil/check-oldies repository on GitHub`_.
#. Clone your fork locally.
#. Set up a virtual environment and activate it.
#. Install the development dependencies::

       $ pip install -r requirements_dev.txt
#. Create a branch for your local development. Do your changes
   locally.
#. Test your changes against the current tests::

       $ pytest
#. If you are adding a feature or fixing a bug, it is good practice to
   add one (or more) specific test(s). Do not hesitate to ask for help
   if you are unsure how to do so.
#. Along with tests, check whether the documentation should be changed
   or augmented.
#. We use a few tools to try to keep an appropriate level of quality
   and style. Run them with::

       $ make quality
#. Once they look good enough, commit your changes and push your
   branch to GitHub.
#. Finally, create a pull request. Try to be clear in the purpose of
   your changes: what they are, why do we need those changes, whether
   there are shortcomings, etc. Remember to provide as much context as
   you can. And if something seems obvious to you, do not hesitate to
   mention it anyway: if it's obvious, it will be easy and quick to
   explain. :) That can save time if the reader does not have the same
   context as you do, which is often the case.
#. Tests and checks of each pull request are automatically run by
   `GitHub Actions`_. You should make sure that the build pass.

Maintainers will try to answer in a timely fashion, but please be
patient and understand that we may have more pressing issues.

.. _Polyconseil/check-oldies repository on GitHub: https://github.com/Polyconseil/check-oldies
.. _GitHub Actions: https://github.com/Polyconseil/check-oldies/actions
