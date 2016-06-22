
=================
    Examples
=================

Let's have a look at a couple of real-life examples for ``idid``.


Config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I have created the following config file to track my work on 
Project X and my Joy of the Day note, that reminds me to stay
optimistic! Small wins make a infinite difference.::

    default_engine: txt:///tmp/logg.txt

    default_journal: general

    journals:
        general:
            desc: Unsorted Activities

        project_x:
            desc: Secrete Project X

        joy:
            desc: Joy of the Day!
            engine: git:///tmp/logg.git


Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's how available command line options for ``idid`` with this
config.:: 

    usage: idid [today|DATE] [topic] '@mention Logg record #tags'

    optional arguments:
      -h, --help      show this help message and exit
      --debug         Turn on debugging output, catch exceptions
      --quiet         Turn off all logging except errors; no exceptions


To save a joy, just run ``idid``::

    > idid joy 'Finished drafting the idid feature'
    > idid joy yesterday 'Cleaned out my inbox'


That's it (for now)! Now you can experiment yourself ;-)
