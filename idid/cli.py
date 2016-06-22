# coding: utf-8

"""
Command line interface for idid

This module takes care of processing command line options and
running the main loop which gathers all individual stats.

Usage, for saving idid logg's::

    idid chores 'Cleaned my inbox #ftw'
    idid proj_x 'Drafted Project X Charter'
    idid yesterday proj_x 'Fixed the leaky pipe'
    idid 2015-05-05T09:00:00 confs 'Attended PyCon CZ in Brno'
    idid 'something amazing today! #lifeisgreat'

If a journal target is not specificed, 'master' will be used.

"""

from __future__ import unicode_literals, absolute_import

import os
import sys
import argparse

from configure import Configuration

import idid.utils as utils
from idid.utils import log
from idid.logg import Logg, DT_ISO_FMT

DEFAULT_IDID_CONFIG = os.path.expanduser('~/.idid/config.yaml')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IDID_USAGE = "idid [today|DATE|...] [journal] '@mention, log record #hash #tag'"


class Options(object):
    """ Command line options parser """

    _config_file = None
    arguments = None

    def __init__(self, arguments=None):
        """ Prepare the shared [i]did argument parser """
        self.parser = argparse.ArgumentParser(usage=IDID_USAGE)
        # if we don't pass args, we can assume we're calling this via CLI
        # so grab the args from sys.argv instead
        self.arguments = arguments or sys.argv[1:]
        log.debug(' ... arguments? {0}'.format(self.arguments))

        # Enable debugging output (even before options are parsed)
        if "--debug" in self.arguments:
            log.setLevel(utils.LOG_DEBUG)
        #  Turn off everything except errors, including warnings
        if "--quiet" in self.arguments:
            log.setLevel(utils.LOG_ERROR)

        # Head / Parent parser (shared)
        # Add Debug option
        self.parser.add_argument(
            "--debug", action="store_true",
            help="Turn on debugging output, do not catch exceptions")

        # Add quiet, which overrides debug if both are issued
        self.parser.add_argument(
            "--quiet", action="store_true",
            help="Turn off all logging except errors; catch exceptions")

        # Add quiet, which overrides debug if both are issued
        self.parser.add_argument(
            "--config-file", type=str, default=DEFAULT_IDID_CONFIG,
            help="Customize the location of the idid yaml config file")

    def parse(self, arguments=None):
        """ Parse the shared [i]did arguments """
        arguments = self.arguments or arguments
        # FIXME: prep/normalize arguments in __init__
        # Split arguments if given as string and run the parser
        if isinstance(arguments, basestring):
            arguments = utils.split(arguments)

        # run the wrapped argparser command to gather user set arg values
        # FROM: https://docs.python.org/3/library/argparse.html
        # Sometimes a script may only parse a few of the command-line
        # arguments, passing the remaining arguments on to another script or
        # program.  In these cases, the parse_known_args() method can be
        # useful. It works much like parse_args() except that it does not
        # produce an error when extra arguments are present. Instead, it
        # returns a two item tuple containing the populated namespace and
        # the list of remaining argument strings.
        opts, _arguments = self.parser.parse_known_args(arguments)

        if not opts.config_file:
            opts.config_file = os.path.expanduser(DEFAULT_IDID_CONFIG)
        opts.config = Configuration().from_file(opts.config_file)
        # alias shortcut
        self.config = opts.config

        # if we're passing arguments in as a string we might get \n's or null
        # strings '' that we want to be sure to ignore
        _arguments = filter(
            lambda x: x if x else None, [_.strip() for _ in _arguments if _])

        # Now let the subclass parse the remaining special opts that
        # weren't consumed by default argparser
        opts = self._parse(opts, _arguments)

        return opts


class LoggOptions(Options):
    """ ``idid`` command line arguments parser """

    def _parse_date(self, dt, fmt=None):
        """ Try to convert a given value to a utils.Date() instance """
        try:
            # test if it's not a datelike instance ...
            _dt = utils.Date(dt, fmt=fmt)
        except ValueError:
            # nope, not a datelike instance
            _dt = None
        return _dt

    def _parse(self, opts, args):
        """ Perform additional check for ``idid`` command arguments """
        k_args = len(args)
        _dt = opts.date = None
        logg = opts.logg = None
        journal = opts.journal = None

        default_journal = self.config.get('default_journal')
        _journals = self.config.get('journals') or {}

        log.debug(' ... got {0} args [{1}]'.format(k_args, args))
        if k_args == 0 and default_journal:
            # launch the editor to save a message into 'default' branch
            # FIXME: 'unsorted' should be configurable as 'default branch'
            log.warn('Target branch not set, using "{0}"'.format(
                default_journal))
            journal, logg = default_journal, '--'

        elif k_args == 1:
            # NOTE: two different usage patterns can be expected here
            # 1) idid journal   # launch EDITOR for logg in target journal
            # 2) idid 'logg record'  # save under default branch 'unsorted'
            # if we have a value that's got more than one word in it, we
            # assume it's a logg (B), otherwise (A)
            arg = args.pop()
            k_words = len(arg.split())
            # variant A); user wants to launch the editor
            # variany B); user wants to save record to 'master' branch
            # default to an unspecified, unsorted target journal since
            # journal not specified
            if k_words == 1:
                journal, logg = (arg, '--')
            elif default_journal:
                journal, logg = (default_journal, arg)
            else:
                raise RuntimeError('UNKNOWN ERROR')

        elif k_args == 2:
            # variants:
            # 1) idid [datetime] 'logg message'
            # 2) idid [datetime] journal  # launch editor
            # 3) idid journal 'logg message'
            # 4) idid unquoted logg message
            _one = args[0].strip()
            _two = args[1].strip()

            # try to parse a date from the value
            _dt = self._parse_date(_one, DT_ISO_FMT)

            if _dt:
                if _two in _journals:
                    # scenario 2)
                    journal, logg = (_two, '--')
                else:
                    # scenario 1)
                    journal, logg = (_two, _one)
            elif _one in _journals:
                # senario 3)
                journal, logg = (_one, _two)
            elif default_journal:
                # senario 4)
                journal, logg = (default_journal, _two)
            else:
                raise RuntimeError("No journal specified.")

        elif k_args >= 3:
            # variants:
            # 1) idid [datetime] journal 'message'
            # 2) idid [datetime] unquoted logg
            # 3) idid journal unquoted logg
            _one = args[0]
            _two = args[1]
            _three = ' '.join(args[2:])

            # try to parse a date from the value
            _dt = self._parse_date(_one, DT_ISO_FMT)

            if _dt:
                if _two in _journals:
                    # scenario 1)
                    journal, logg = (_two, _three)
                elif default_journal:
                    # scenario 2)
                    journal, logg = (_two, ' '.join(args[1:]))
                else:
                    raise RuntimeError("No journal specified.")
            elif _one in _journals:
                # senario 3)
                journal, logg = (_one, ' '.join(args[1:]))
            elif default_journal:
                # senario 4)
                journal, logg = (default_journal, ' '.join(args[:]))
            else:
                raise RuntimeError("No journal specified.")

        else:
            raise RuntimeError("Ambiguous command line arguments!")

        opts.date = _dt or utils.Date('today', fmt=DT_ISO_FMT)
        opts.journal = journal
        opts.logg = logg
        log.debug(' Found Date: {0}'.format(_dt))
        log.debug(' Found Target: {0}'.format(journal))
        log.debug(' Found Logg: {0}'.format(logg))
        return opts


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def main(arguments=None, config=None):
    """
    Parse arguments for ``idid`` command.

    Pass optional parameter ``arguments`` as either command line
    string or list of options. This is mainly useful for testing.

    ``config`` can be passed in as a path or string to access user defined
    values for important variables manually. YAML only.

    Returns the saved logg string.

    """
    # Parse options, initialize gathered stats
    options = LoggOptions(arguments=arguments).parse()

    # FIXME: pass in only config; set config.journal = options.journal
    if not config:
        config = options.config_file

    logg = Logg(config, options.journal)

    return logg.logg_record(options.logg, options.date)
