# coding: utf-8
# @ Author: "Chris Ward" <cward@redhat.com>

""" Tests for the command line script """

from __future__ import unicode_literals, absolute_import

import os
import re
import sys
import pytest

from configure import ConfigurationError

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Constants
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Prepare path and config examples
PATH = os.path.dirname(os.path.realpath(__file__))
EXAMPLE_CONFIG = PATH + "/../examples/config.yaml"

_logg = "idid joy test 1 2 3"
_date = "2015-10-21T07:28:00"
# _date = "2015-10-21T07:28:00 +0000"
ARGS_OK_TXT = [_date, "project_x", _logg]
ARGS_OK_GIT = [_date, "joy", _logg]
ARGS_BAD_JOURNAL = [_date, "not_in_config", _logg]
ARGS_NO_DATE = ["joy", _logg]

TMP_TXT = '/tmp/logg.txt'

TMP_GIT = '/tmp/logg.git'

RESULT_OK_MIN = "<project_x> [2015-10-21]:: idid joy test 1 2 3"
# NOTE git version 1.8 doesn't include the Date: ... line
# git 2.4 does
# FIXME: conditionally check the line according to git version
# RESULT_OK_GIT = re.compile(r'\[joy \w+\] idid logg joy test 1 2 3\n '
#                           'Date: Wed Oct 21 07:28:00 2015 \+0000')
# RESULT_OK_GIT = re.compile(r'\[joy \w+\] idid logg joy test 1 2 3')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  idid Test Environment Set-up
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import idid.cli
import idid.logg

# We are running pytest, so there will be args present
# sys.argv which need to be removed to simulate an actual
# exec of idid from the cli since the parser falls back to check
# args in sys.argv because of the use of argparser's argparse
# command in idid.cli
# ...
# opt, arg = self.parser.parse_known_args(arguments)
# ...
cmd = sys.argv[0]
assert 'py' in cmd and 'test' in cmd

fake_argv = ['/bin/idid']
sys.argv = fake_argv


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Utils
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def check_gitlogg_commit_k(x, config, journal):
    # check the expected number of commits have been made
    l = idid.logg.GitLogg(config=config, journal=journal)
    commits = list(l._logg_repo.iter_commits())
    assert len(commits) == x


def clean_git(path):
    idid.utils.remove_path(path)
    assert not os.path.exists(path)
    # clear all stale GIT environ variables
    # WARNING DESTRUCTIVE! but when running tests from Make during pre-commit
    # git hook, it seems GitPython gets all confused because of env vars...
    # _vars = os.environ.keys()
    # for var in _vars:
    #    if var[:3] == 'GIT':
    #        os.environ.pop(var)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_default_no_args_cli():
    # loading from a file that doesn't exist should cause idid to except
    assert not os.path.exists('/bla/bla.yaml')
    with pytest.raises(ConfigurationError):
        idid.cli.main(config='/bla/bla.yaml')

    try:
        # touch the config file, now when we run it again,
        with open('/tmp/empty', 'w') as f:
            f.write('')
        # it will still crash because it's 'invalid' config
        with pytest.raises(ConfigurationError):
            idid.cli.main(config='/tmp/empty')

        # touch the config file, now when we run it again,
        with open('/tmp/empty', 'w') as f:
            f.write('invalid YAML: -- {} ')
        # it will still crash because it's 'invalid' config
        with pytest.raises(ConfigurationError):
            idid.cli.main(config='/tmp/empty')
    finally:
        idid.utils.remove_path('/tmp/empty')

    idid.cli.main(config=EXAMPLE_CONFIG)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Logg
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_default_logg():
    clean_git(TMP_TXT)
    r = idid.cli.main(ARGS_OK_TXT, EXAMPLE_CONFIG)
    assert os.path.exists(TMP_GIT)
    assert r == RESULT_OK_MIN


def test_default_git_logg():
    clean_git(TMP_GIT)
    r = idid.cli.main(ARGS_OK_GIT, EXAMPLE_CONFIG)
    assert os.path.exists(TMP_GIT)
    # assert RESULT_OK_GIT.search(r)
    # FIXME: This doesn't check for the correct datetime!
    assert re.match('\[joy \w+\]', r)
    check_gitlogg_commit_k(1, EXAMPLE_CONFIG, 'joy')


def test_topic_not_configed():
    clean_git(TMP_GIT)
    with pytest.raises(ConfigurationError):
        idid.cli.main(ARGS_BAD_JOURNAL, EXAMPLE_CONFIG)
    check_gitlogg_commit_k(1, EXAMPLE_CONFIG, 'joy')


def test_logg_api():
    clean_git(TMP_GIT)
    # running this should be OK by default (strict == False)
    r = idid.cli.main(ARGS_NO_DATE, EXAMPLE_CONFIG)
    # %d comes back as 01 but git doesn't zero-pad the days
    # so on a day like first of november %d is 01 but git shows just 1
    assert re.match('\[joy \w+\]', r)

    # git version 1.8 doesn't include the Date: ... string in the summary
    # git version 2.4 does; FIXME: need to conditionally check this depending
    # on git version installed ...
    # now = idid.base.Date().date.strftime("%a %b")
    # assert re.search(now, r)


# with pytest.raises(idid.base.OptionError):

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Report
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def test_help_example():
    """ Help message with example config """
    with pytest.raises(SystemExit):
        idid.cli.main(["--help"], config=EXAMPLE_CONFIG)
