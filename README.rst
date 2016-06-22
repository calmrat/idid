
======================
    idid
======================

Logg, save and share your daily activities with ease!


Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comfortably store and share daily activities, including status 
report data for projects, etc and share the results with your
friends, colleagues and the world using Git.


Synopsis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage for saving stats to configured Git Repo is straightforward::

    idid [today|yesterday|YYYY-MM-DD] [journal] 'logg msg'

Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Save yesterday's completed activity for Project X::

    idid yesterday project_x Drafted Project Charter #complete

Save an activity you completed today (default journal: general):: 

    idid Got my driver's license! #woot

Celebrate the joy of the day::

    idid joy @kejbaly2 told me I'm special! <3


Utils
-----

Use ``--debug`` or set the environment variable
``DEBUG`` to 1 through 5 to set the desired level of debugging.

--config=FILE
    Use alternate configuration file (default: 'config')

--debug
    Turn on debugging output, do not catch exceptions

See ``idid --help`` for complete list of available options.



Install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

or use PIP (sudo required if not in a virtualenv)::

    pip install idid

See documentation for more details about installation options.


Config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The config file ``~/.idid/config.yaml`` is used to store both 
general settings and configuration of individual journals::

    default_engine: txt:///tmp/logg.txt
    default_journal: general
    #gpg: 1C725D56
    journals:
        general:
            desc: Unsorted Activities

        project_x:
            desc: Secrete Project X

        joy:
            desc: Joy of the Day!
            engine: git:///tmp/logg.git


Links
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Git:
https://github.com/kejbaly2/idid

Docs:
http://idid.readthedocs.org

Issues:
https://github.com/kejbaly2/idid/issues

Releases:
https://github.com/kejbaly2/idid/releases

PIP:
https://pypi.python.org/pypi/idid


Authors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chris Ward

Forked from Petr Šplíchal's https://github.com/psss/did project.


Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://badge.fury.io/py/idid.svg
    :target: http://badge.fury.io/py/idid

.. image:: https://travis-ci.org/kejbaly2/idid.svg?branch=master
    :target: https://travis-ci.org/kejbaly2/idid

.. image:: https://coveralls.io/repos/kejbaly2/idid/badge.svg
    :target: https://coveralls.io/r/kejbaly2/idid

.. image:: https://img.shields.io/pypi/dm/idid.svg
    :target: https://pypi.python.org/pypi/idid/

.. image:: https://img.shields.io/pypi/l/idid.svg
    :target: https://pypi.python.org/pypi/idid/

.. image:: https://readthedocs.org/projects/idid/badge/
    :target: https://readthedocs.org/projects/idid/
