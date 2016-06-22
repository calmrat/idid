#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: "Chris Ward" <cward@redhat.com>

from __future__ import unicode_literals, absolute_import

from datetime import date, datetime

import pytz
import pytest


def test_utils_import():
    # simple test that import works
    from idid import utils
    assert utils


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Constants
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_email_re():
    ''' Confirm regex works as we would expect for extracting
        name, login and email from standard email strings'''
    from idid.utils import EMAIL_REGEXP

    # good
    x = '"Chris Ward" <cward@redhat.com>'
    groups = EMAIL_REGEXP.search(x).groups()
    assert len(groups) == 2
    assert groups[0] == 'Chris Ward'
    assert groups[1] == 'cward@redhat.com'

    x = 'cward@redhat.com'
    groups = EMAIL_REGEXP.search(x).groups()
    assert len(groups) == 2
    assert groups[0] is None
    assert groups[1] == 'cward@redhat.com'

    # bad
    x = 'cward'
    groups = EMAIL_REGEXP.search(x)
    assert groups is None

    # ugly
    x = '"" <>'
    groups = EMAIL_REGEXP.search(x)
    assert groups is None


def test_log():
    from idid.utils import log
    assert log
    log.name == 'idid'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Utils
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_header():
    from idid.utils import header
    assert header


def test_shorted():
    from idid.utils import shorted
    assert shorted


def test_item():
    from idid.utils import item
    assert item


def test_pluralize():
    from idid.utils import pluralize
    assert pluralize
    assert pluralize("word") == "words"
    assert pluralize("bounty") == "bounties"
    assert pluralize("mass") == "masses"


def test_listed():
    from idid.utils import listed
    assert listed
    assert listed(range(1)) == "0"
    assert listed(range(2)) == "0 and 1"
    assert listed(range(3), quote='"') == '"0", "1" and "2"'
    assert listed(range(4), max=3) == "0, 1, 2 and 1 more"
    assert listed(range(5), 'number', max=3) == "0, 1, 2 and 2 more numbers"
    assert listed(range(6), 'category') == "6 categories"
    assert listed(7, "leaf", "leaves") == "7 leaves"
    assert listed([], "item", max=0) == "0 items"


def test_ascii():
    from idid.utils import ascii
    assert ascii
    assert ascii("ěščřžýáíé") == "escrzyaie"
    assert ascii(0) == "0"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Logging
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_eprint():
    from idid.utils import eprint
    assert eprint


def test_info():
    from idid.utils import info
    assert info
    info("something")
    info("no-new-line", newline=False)


def test_Logging():
    from idid.utils import Logging
    assert Logging


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Coloring
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_Coloring():
    from idid.utils import Coloring
    assert Coloring


def test_color():
    from idid.utils import color
    assert color
UTC = pytz.utc
CET = pytz.timezone('CET')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Date
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_today():
    from idid.utils import today

    # FIXME: not, resolution isn't correct, but still...
    d = today().date()
    _d = datetime.utcnow().replace(tzinfo=pytz.utc).date()
    assert d == _d


def test_Date_type_handling():
    from idid.utils import Date

    # clearly not dates
    BAD_DATES = [int(1), 'BAD DATE']
    for bad in BAD_DATES:
        with pytest.raises(ValueError):
            Date(bad)

    # Date, no timezone or time even
    D_today = date(2015, 1, 1)
    d_today = '2015-01-01'
    assert unicode(Date(d_today)) == d_today
    assert unicode(Date(D_today)) == d_today
    # should always have utc timezone attached
    assert Date(d_today).date.tzinfo == pytz.utc

    # UTC
    DT_today_utc = datetime(2015, 1, 1, 0, 0, 0, tzinfo=UTC)
    dt_today_utc = '2015-01-01 00:00:00.000 +0000'
    assert unicode(Date(dt_today_utc)) == d_today
    # should always have utc timezone attached
    # so this is the last time we test for it since it's been found 2x already
    assert Date(dt_today_utc).date.tzinfo == pytz.utc

    # UTC using 'T' instead of ' ' (space) between date and time
    dt_today_utc = '2015-01-01T00:00:00.000 +0000'
    #                         ^
    assert unicode(Date(dt_today_utc)) == d_today
    DT_today_utc = datetime(2015, 1, 1, 0, 0, 0, tzinfo=UTC)
    # Try with datetime
    assert unicode(Date(DT_today_utc)) == d_today

    # CET
    DT_today_cet = datetime(2015, 1, 1, 0, 0, 0, tzinfo=CET)
    dt_today_cet = '2015-01-01 00:00:00.000 +0200'
    d_today_UTC_from_CET = '2014-12-31'
    assert unicode(Date(dt_today_cet)) == d_today_UTC_from_CET
    assert unicode(Date(DT_today_cet)) == d_today_UTC_from_CET

    # UNSPECIFIED timezone (assumed UTC)
    DT_today_x = datetime(2015, 1, 1, 0, 0, 0)
    dt_today_x = '2015-01-01 00:00:00'
    assert unicode(Date(dt_today_x)) == d_today
    assert unicode(Date(DT_today_x)) == d_today

    # CET specific time, 12:00:00
    dt_today_noon_cet = '2015-01-01 12:00:00 +0200'
    iso = '%Y-%m-%d %H:%M:%S %z'

    _DT = unicode(Date(dt_today_noon_cet, fmt=iso))
    dt_today_noon_cet_as_utc = '2015-01-01 10:00:00 +0000'
    assert _DT == dt_today_noon_cet_as_utc


def test_Date_format():
    from idid.utils import Date

    d = '2015-01-01'
    dt = '2015-01-01 00:00:00'
    dtz = '2015-01-01 00:00:00 +0000'
    dtz_cet = '2015-01-01 00:00:00 +0200'
    # since we're 2 hours ahead, in UTC we're 2 behind
    dtz_cet_utc = '2014-12-31 22:00:00 +0000'
    d_cet_utc = '2014-12-31'

    # Default format will return the date in YYYY-MM-DD form
    # after date conversion from defined timezone to UTC, if
    # timezone is set on the incoming date value.
    assert str(Date(d)) == d
    assert str(Date(dt)) == str(d)
    assert str(Date(dtz)) == str(d)
    assert str(Date(dtz_cet)) == str(d_cet_utc)

    # different formats should all work as strftime() expects
    fmt = '%Y'
    assert str(Date(d, fmt=fmt)) == '2015'
    fmt = '%Y-%m-%d'
    assert str(Date(d, fmt=fmt)) == d
    fmt = '%Y-%m-%d %H:%M:%S'
    assert str(Date(dt, fmt=fmt)) == dt
    fmt = '%Y-%m-%d %H:%M:%S %z'
    assert str(Date(dt, fmt=fmt)) == dtz
    assert str(Date(d, fmt=fmt)) == dtz

    # unicode works as expected
    assert unicode(Date('2015-01-01')) == unicode(d)

    # specify timezone
    iso = '%Y-%m-%d %H:%M:%S %z'
    assert unicode(Date(dtz_cet, fmt=iso)) == dtz_cet_utc
