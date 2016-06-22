# coding: utf-8

from __future__ import unicode_literals, absolute_import

import logging
import os
import pytest
import re

from configure import ConfigurationError

# simple test that import works
from idid import utils
from idid.logg import Logg, GitLogg

utils.log.setLevel(logging.DEBUG)

# Prepare path and config examples
PATH = os.path.dirname(os.path.realpath(__file__))
EG_CONF_PATH = PATH + "/../examples/config.yaml"

# default repo is created in ~/.idid/loggs
# OVERRIDE THE ENGINE PATE so we don't destroy the user's actual
# db on accident
DEFAULT_ENGINE_PATH = '/tmp/logg.txt'
GIT_ENGINE_PATH = '/tmp/logg.git'

DEFAULT_ENGINE_URI = 'txt://{0}'.format(DEFAULT_ENGINE_PATH)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Sanity
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_bad_args():
    # Empty Args;
    with pytest.raises(TypeError):
        # config and journal args are required
        Logg()
    with pytest.raises(TypeError):
        # config karg is required
        Logg(journal='joy')
    with pytest.raises(TypeError):
        # journal arg is required
        Logg(EG_CONF_PATH)
    with pytest.raises(TypeError):
        # journal karg is required
        Logg(config=EG_CONF_PATH)

    # Bad config args
    with pytest.raises(ConfigurationError):
        Logg(config=1, journal='joy')
    with pytest.raises(ConfigurationError):
        Logg(config=None, journal='joy')
    with pytest.raises(ConfigurationError):
        Logg(config='blabla', journal='joy')

    # Bad journal args
    with pytest.raises(ConfigurationError):
        Logg(config=EG_CONF_PATH, journal='not_defined')


def test_good_args():
    Logg(config=EG_CONF_PATH, journal='joy')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Unit
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def test_default_logg():
    utils.remove_path(DEFAULT_ENGINE_PATH)
    # ## FIXTURE ## #
    # load a log instance, but it shouldn't create a
    # repo yet, it's lazy
    l = Logg(EG_CONF_PATH, 'project_x')
    # repo will be created only if commit is called
    # which then should create the repo if it doesn't exist
    assert not os.path.exists(DEFAULT_ENGINE_PATH)
    # ## FIXTURE ## #

    ARGS = [
        "test 1 2 3", '2015-10-21T07:28:00 +0000'
    ]

    assert l.logg_record(*ARGS) == "<project_x> [2015-10-21]:: test 1 2 3"

    # now the repo should exist
    assert os.path.exists(DEFAULT_ENGINE_PATH)


def test_git_logg():
    utils.remove_path(GIT_ENGINE_PATH)

    # Example config has 'joy' journal set as git
    l = GitLogg(EG_CONF_PATH, 'joy')

    ARGS = [
        "test 1 2 3", '2015-10-21T07:28:00 +0000'
    ]

    r = l.logg_record(*ARGS)

    # NOTE git version 1.8 doesn't include the Date: ... line
    # git 2.4 does
    RESULT_OK_GIT = re.compile(r'\[joy \w+\] test 1 2 3')

    # the sha changes
    assert RESULT_OK_GIT.match(r)

    commits = list(l._logg_repo.iter_commits())
    assert len(commits) == 1

# test

# ... that default branch is created 'master' if no other journals (branches)
# configured in config file

# ... that only branches defined in config or master can be used
