
==============
    Config
==============

The config file ``~/.idid/config.yaml`` is used to store general
settings and configuration of journals repos. Command line
option ``--config`` allows to select a different config file from
the config directory.

Use the ``IDID_DIR`` environment variable to override the default
config directory ``~/.idid`` and use your custom location instead.
For example if you prefer to keep you home directory clean you
might want to add the following line into ``.bashrc``::

    export DID_DIR=~/.config/idid/


Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's an example config file with all available plugins enabled.

.. literalinclude:: ../examples/config.yaml
    :language: yaml
