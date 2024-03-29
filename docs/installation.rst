Installation
============

You must have Python 3.7 or later, and a relatively recent version of
Git. Git 2.1.4 (shipped with Debian Jessie) is known to work. More
recent versions should work and are supported.

Install with ``pip``, preferably in a `virtual environment`_:

.. code-block:: bash

    $ python3 -m venv /path/to/your/virtualenv
    $ source /path/to/your/virtualenv/bin/activate
    $ pip install "check-oldies[toml]"


.. note::

    If you do not need to read TOML configuration files, you may omit the
    optional dependency and install like this:

    .. code-block:: bash

        $ pip install check-oldies

    Configuration files are not required, but some options are only
    available through configuration files. If you are not sure, do not
    use the latter command. Instead, use ``pip install check-oldies[toml]``
    as indicated above.


.. _virtual environment: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments
