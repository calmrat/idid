
===============
    Install
===============

Fedora
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Fedora simply install the package::

    dnf install idid

That's it! :-)


PIP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic dependencies for buiding/installing pip packages::

    sudo yum install gcc
    sudo yum install python-devel python-pip python-virtualenv

Upgrade to the latest pip/setup/virtualenv installer code::

    sudo pip install --upgrade pip setuptools virtualenv

Install into a python virtual environment (OPTIONAL)::

    virtualenv ~/idid
    source ~/idid/bin/activate

Install idid (sudo required if not in a virtualenv)::

    pip install idid

See the `pypi package index`__ for detailed package information.

__ https://pypi.python.org/pypi/idid
