# coding: utf-8
# @ Author: "Chris Ward" <cward@redhat.com>

""" Tests for the command line script """

from __future__ import unicode_literals, absolute_import

import os
import re
import sys
import tempfile
import pytest

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Constants
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Prepare path and config examples
PATH = os.path.dirname(os.path.realpath(__file__))
# copy/paste from idid.base.Config.example()
MINIMAL = ""
EXAMPLE = "".join(open(PATH + "/../examples/config.yaml").readlines())
# Substitute example git paths for real life directories
#EXAMPLE = re.sub(r"\S+/git/[a-z]+", PATH, EXAMPLE)

_logg = "idid joy test 1 2 3"
_date = "2015-10-21T07:28:00 +0000"
ARGS_OK_MIN = [_date, "joy", _logg]
ARGS_TOPIC_NO_CONFIG = [_date, "not_in_config", _logg]
ARGS_NO_DATE = ["joy", _logg]
ARGS_NO_DATE_NO_TOPIC = [_logg]

RESULT_OK_MIN = "2015-10-21 idid joy test 1 2 3 [joy]"
# NOTE git version 1.8 doesn't include the Date: ... line
# git 2.4 does
# FIXME: conditionally check the line according to git version
#RESULT_OK_GIT = re.compile(r'\[joy \w+\] idid logg joy test 1 2 3\n '
#                           'Date: Wed Oct 21 07:28:00 2015 \+0000')
RESULT_OK_GIT = re.compile(r'\[joy \w+\] idid logg joy test 1 2 3')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  idid Test Environment Set-up
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# OVERRIDE DEFAULT IDID CONFIG TO AVOID USING USER'S PERSONAL CONFIG FILE
tmpd = tempfile.mkdtemp()
os.environ['IDID_DIR'] = tmpd

TMP_CONFIG = os.path.join(tmpd, 'config')

import idid.cli

import idid.base

import idid.logg
# avoid using the default engine dir in case user has something there...
idid.logg.DEFAULT_ENGINE_DIR = tmpd

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

def check_gitlogg_commit_k(x, config=GOOD_GIT_CONFIG):
    # check the expected number of commits have been made
    l = idid.logg.GitLogg(config=config)
    commits = list(l.logg_repo.iter_commits())
    assert len(commits) == x


def clean_git():
    idid.utils.remove_path(GIT_ENGINE_PATH)
    assert not os.path.exists(GIT_ENGINE_PATH)
    # clear all stale GIT environ variables
    # WARNING DESTRUCTIVE! but when running tests from Make during pre-commit
    # git hook, it seems GitPython gets all confused because of env vars...
    _vars = os.environ.keys()
    for var in _vars:
        if var[:3] == 'GIT':
            os.environ.pop(var)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# NOTE: and calls to main() will auto set idid.base.IDID_CONFIG!

def test_default_no_args_cli():
    idid.utils.remove_path(GIT_ENGINE_PATH)

    # when config is None idid defaults to using idid.base.CONFIG
    # default config path and depending on if this config file exists or not
    # idid might print out a default report
    # Since this is a test, we want to avoid using the default idid config
    # though just in case the testing user is running in his 'production' env

    # We changed the idid.base.CONFIG to a random temporary directory in the
    # header. See line 66 or so...

    # loading from a file that doesn't exist should cause idid to except
    assert not os.path.exists(TMP_CONFIG)
    with pytest.raises(idid.base.ConfigError):
        idid.cli.main()

    # touch the config file, now when we run it again,
    with open(TMP_CONFIG, 'w') as f:
        f.write('')
    # it will still crash because of an invalid conf (missing general section)
    with pytest.raises(idid.base.ConfigError):
        idid.cli.main(TMP_CONFIG)

    # include the minimum config [general] section with email = ...
    # which should now make main() pass
    with open(TMP_CONFIG, 'w') as f:
        f.write(BASE_CONFIG)
    idid.cli.main(TMP_CONFIG)

    idid.utils.remove_path(TMP_CONFIG)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Logg
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_default_logg():
    clean_git()
    r = idid.cli.main(ARGS_OK_MIN, GOOD_LOG_CONFIG)
    assert os.path.exists(DEFAULT_ENGINE_PATH)
    assert r == RESULT_OK_MIN


def test_default_git_logg():
    clean_git()
    r = idid.cli.main(ARGS_OK_MIN, GOOD_GIT_CONFIG)
    assert os.path.exists(GIT_ENGINE_PATH)
    assert RESULT_OK_GIT.search(r)
    check_gitlogg_commit_k(2)


def test_topic_not_configed():
    clean_git()
    idid.cli.main(ARGS_TOPIC_NO_CONFIG, GOOD_GIT_CONFIG)
    check_gitlogg_commit_k(3)


def test_logg_api():
    clean_git()
    # running this should be OK by default (strict == False)
    r = idid.cli.main(ARGS_NO_DATE, GOOD_GIT_CONFIG)
    # %d comes back as 01 but git doesn't zero-pad the days
    # so on a day like first of november %d is 01 but git shows just 1
    assert re.match('\[joy \w+\]', r)

    # git version 1.8 doesn't include the Date: ... string in the summary
    # git version 2.4 does; FIXME: need to conditionally check this depending
    # on git version installed ...
    #now = idid.base.Date().date.strftime("%a %b")
    #assert re.search(now, r)

    # strict = False by default, so this shouldn't fail
    r = idid.cli.main(ARGS_NO_DATE_NO_TOPIC, GOOD_GIT_CONFIG)

    # test that the journal topic is 'unsorted'
    assert re.match('\[unsorted \w+\]', r)

    # this fails since
    # 'unsorted' isn't defined in config
    check_gitlogg_commit_k(3)


# with pytest.raises(idid.base.OptionError):

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Report
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def test_help_minimal():
    """ Help message with minimal config """
    with pytest.raises(SystemExit):
        idid.cli.main(["--help"], MINIMAL)


def test_help_example():
    """ Help message with example config """
    idid.base.Config(config=EXAMPLE)
    with pytest.raises(SystemExit):
        idid.cli.main(["--help"])
