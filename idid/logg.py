# coding: utf-8
# @ Author: "Chris Ward" <cward@redhat.com>

from __future__ import unicode_literals, absolute_import

import os
import re
from subprocess import call
import tempfile

from configure import Configuration, ConfigurationError

from idid.utils import log, Date, today

try:
    import git
except ImportError:
    log.warn('GitPython not installed!')
    git = None

""" Logg, save and share your daily activities! """

"""
Overview
--------
``idid`` logg's can be stored in

 * plain text file (txt; DEFAULT)
 * git commits repo
  - journal (topic) are branches
  - loggs are commits
  - can be 'cloned' and shared
"""

DT_ISO_FMT = "%Y-%m-%dT%H:%M:%S %z"
DT_GIT_FMT = "%Y-%m-%dT%H:%M:%S"

# Regex's
URI_RE = re.compile('([\w]*)://(.*)')

# only git backend supported; not sure why, but I think
# we might want to extend to support other 'backends' somehow
SUPPORTED_BACKENDS = ['txt']
if git:
    # only enable git backend if PythonGit is installed
    SUPPORTED_BACKENDS += ['git']

LOGG_CONFIG_KEY = 'logg'

COMMENT_RE = re.compile('^#')

LOGG_EDITOR = os.environ.get('EDITOR', 'vim')
# explain to the user that they are in a idid git message editor
DEFAULT_LOGG_RECORD = """


# Please enter a idid logg for the activities you completed on [{date}].
# Lines starting with '#' will be ignored, and an empty message
# aborts the commit.
#
# Saving idid logg to [{journal}] branch
#
# Summary line must be
# * no more than 50c
# * separated from the body with a empty-line
"""


"""
# EXAMPLE CLI USAGE

    idid yesterday joy "@kejbaly2 merged all my PRs! #idid #FTW"

# EXAMPLE MODULE USAGE

    >>> from idid import logg
    >>> l = logg.Logg(config)
    >>> l.logg_record('joy', '@kejbaly2 merged my pull requests!', 'yesterday')

# EXAMPLE CONFIG (YAML)

    default_engine: txt:///tmp/logg.txt

    project_x:
    desc: Secrete Project X

    joy:
        - engine: git:///tmp/logg.git
        desc: Joy of the Day!


Logg Record can for example contain (for later parsing)::

 * any arbitrary text
 * @mention's to reference another user
 * #tags to include additional reference to shared theme or topic

With ``GitLogg`` backend it is also possible to save multiline logg messages.
eg::

    idid joy --   # launch $EDITOR

    Summary (50c max), with body separated by \n

    This is the detailed version of the idid logg message that
    describes in more detail what actually happened...
"""

# FIXME: invidual but related idids on a single line separated by semi-colon


class LoggFactory(type):
    """ Detect the type of backend based on the engine uri and
        return the backend expected class automatically
    """
    def __call__(cls, config, journal):
        try:
            if not config:
                raise ConfigurationError("Config can't be null")
            elif isinstance(config, Configuration):
                pass
            elif isinstance(config, dict):
                config = Configuration.from_dict(config).configure()
            elif isinstance(config, (str, unicode)):
                if os.path.exists(config):
                    # config is a valid /existing path
                    config = os.path.abspath(config)
                    config = Configuration.from_file(config).configure()
                else:
                    # config is loaded as a simple string
                    config = Configuration.from_string(config).configure()
            else:
                raise ConfigurationError(
                    'Failed to load config file [{0}]'.format(config))
        except Exception as err:
            raise ConfigurationError(err)

        if 'journals' not in config:
            # User tried using an unconfigured journal
            raise ConfigurationError('No journals configured!')
        elif journal not in config['journals']:
            # User tried using an unconfigured journal
            raise ConfigurationError(
                'Invalid journal: {0}'.format(journal))
        if 'default_engine' not in config:
            # RAISE if engine isn't defined!
            raise ConfigurationError('default_engine must be configured!')
        else:
            # determine which Logg Class to load
            _cls = Logg._get_Logg_Type(config, journal)
            return type.__call__(_cls, config, journal)


class Logg(object):
    """ idid logg backend class for storing idid messages """
    __metaclass__ = LoggFactory
    _engine = None
    _engine_path = None
    _engine_backend = None
    _journal = None
    _journal_config = None
    _logg_repo = None
    _logg_format = '<{journal}> [{date}]:: {record}'
    config = None

    def __init__(self, config, journal):
        # load the journal specific engine or default_engine
        _default_engine = config.get('default_engine')

        self.config = config
        self._journal = journal

        self._journal_engine = config['journals'][journal].get(
            'engine', _default_engine)

        self._engine_backend, self._engine_path = self._parse_engine(
            self._journal_engine)

    @staticmethod
    def _get_Logg_Type(config, journal):
        # Parse out the engine type
        jconf = config['journals'][journal]
        if 'engine' not in jconf:
            engine = config['default_engine']
            log.debug(
                'Engine not defined for Journal [{0}]. Using [{1}]'.format(
                    journal, engine))
        else:
            engine = jconf['engine']
            log.debug('LoggFactory loading [{0}]...'.format(engine))

        backend, path = Logg._parse_engine(engine)

        _cls = GitLogg if backend == 'git' else Logg
        log.debug(' ... Loading Backend Class: {0}'.format(_cls))
        return _cls

    @staticmethod
    def _parse_engine(engine):
        """ Parse the engine uri to determine where to store loggs """
        engine = (engine or '').strip()
        backend, path = URI_RE.match(engine).groups()

        if backend not in SUPPORTED_BACKENDS:
            raise NotImplementedError(
                "Logg supports only {0} for now.".format(SUPPORTED_BACKENDS))
        log.debug('Found engine: {0}'.format(engine))
        return backend, path

    def logg_record(self, record, date=None):
        if not record:
            raise RuntimeError(
                "record [{1}] must be defined".format(record))
        # we want to store dates in txt as YYYY-MM-DD which is default
        # formate for Date() objects
        date = unicode(Date(date or today()))

        record = record.decode('utf-8').strip()
        # default format YYYY-MM-DD
        log.debug('Saving idid Logg("{0}", "{1}", "{2}")'.format(
            self._journal, record, date))
        result = self._logg_record(record, date)
        log.info('SUCCESS: \n{0}'.format(result))
        return result

    def _logg_record(self, record, date):
        # self._engine_path contains the path part of the engine uri
        mode = 'a' if os.path.exists(self._engine_path) else 'w'
        with open(self._engine_path, mode) as stdout:
            result = self._logg_format.format(
                date=date, record=record, journal=self._journal)
            stdout.write(result)
        return result


class GitLogg(Logg):

    """ idid logg backend to save loggs to a git repo """

    def __init__(self, *args, **kwargs):
        super(GitLogg, self).__init__(*args, **kwargs)
        # cache the _logg_repo in the instance
        self._logg_repo = self._load_repo()

    def _logg_record(self, record, date):
        """
        # %> idid work 2015-01-01 '... bla bla #tag @mention ...'
        # results in a logg entry in the 'work' datastore for $DATE (by user)

        # author_date = '2015-01-01T01:01:01'
        # record = 'Did something AMAZING! [#id] #did'

        # info about specifying a specific date for the committ
        # http://stackoverflow.com/a/3898842/1289080
        # Each commit has two dates: the author date and the committer date.

        # commit the record and update the commit date to
        # r.git.commit(m=record, date=author_date, allow_empty=True)
        """
        # FIXME: take emails from config (extracted in CLI already)
        # FIXME: extract out the possible dates and other tokens
        # FIXME: check that we're using the write dates here...
        # FIXME: check if it isn't a duplicate... of the previous
        # and abort usless it's forced
        #
        # git date option needs HH:MM:SS +0000 specified too or it will assume
        # current time values instead of 00:00:00
        #
        # When passing this I get a commit on
        #  Date: Thu Jan 1 09:32:32 2015 +0100
        # when just passing utcnow() i get
        #  Date: Sun Oct 11 08:31:51 2015 +0200
        # according to my clock (CET; +0200) it's Oct 11 10:33:...

        # Make absolutely sure we have a git 1.8+ compatible date format!
        date = Date(date, fmt=DT_GIT_FMT)
        # Build dict for sending as args to the git commend
        # -- or null says we want to open our editor to edit the commit msg

        try:
            result = self._commit(self._journal, record, date)
        except KeyboardInterrupt as err:
            log.error('Error encountered during git commit: {0}'.format(err))
            raise SystemExit('\n\n')

        # FIXME #########
        # LOAD SYNC_TO options from config PER JOURNAL
        # ie, sync to remote (friends) journals too
        # ENABLE syncing to multiple (remotee) branches
        #sync_to = None
        #if sync_to:
        #    # sync/backup branch (eg, master or remote)
        #    log.info(' ... ... also syncing to: {0}'.format(sync_to))
        #    record = '{0} [{1}]'.format(record, self._journal)
        #    result_sync = self._commit(record, date)
        #    log.debug(" ... ... record committed\n{0}".format(result_sync))

        return result

    # FIXME: sync; sync_tx == remotee, remotees
    def _commit(self, branch, record, date):
        if record in ['--', None]:
            # inspired by: http://stackoverflow.com/a/6309753/1289080
            with tempfile.NamedTemporaryFile(suffix=".tmp") as _tmp:
                _n = _tmp.name
                description = DEFAULT_LOGG_RECORD.format(
                    **dict(journal=self._journal, date=date))
                _tmp.write(description)
                _tmp.flush()
                call([LOGG_EDITOR, _n])
                record = [x.strip(' ') for x in open(_n).readlines() if x]
                record = [x for x in record if not COMMENT_RE.match(x)]
                k_lines = len(record)
                if k_lines > 1:
                    # complain that we expect the SUMMARY / MSG BODY form
                    if not record[1] == '\n':
                        raise RuntimeError(
                            'Invalid format. Usage:\nSUMMARY\n\nMESSAGE...')
                record = ''.join(record).strip()
                if not record:
                    raise SystemExit('Empty Logg. Aborting.')

        # git command kwargs
        kwargs = dict(date=date, allow_empty=True)

        # Include the record in the git command too
        kwargs['m'] = record

        # FIXME: add documentation to describe this config option
        # if gpg key is defined in .config [logg], git will attempt to
        # sign the commits with the provided key
        gpg_sign = self.config.get('gpg', None)
        if gpg_sign:
            kwargs['gpg_sign'] = gpg_sign

        try:
            # checkout the journal branch, but make sure to return to
            # pre-commit state after completion (clean-up) ...
            current = self._logg_repo.active_branch

            log.debug("Checking out branch: {0}".format(branch))
            self._checkout_branch(branch)

            # HACK !!!!
            # os.environ["GIT_COMMITTER_DATE"] = str(date)

            r = self._logg_repo.git.commit(**kwargs)
            log.debug(" ... record committed")

        finally:
            if self._logg_repo.active_branch != current:
                log.debug(
                    " ... cleaning up (git checkout {0}...)".format(current))
                self._checkout_branch(current)
        return r

    def _checkout_branch(self, branch=None):
        branch = branch or 'master'
        # Try to create the journal branch
        try:
            self._logg_repo.git.checkout(branch, b=True)
        except git.GitCommandError:
            # branch already exists, so check it out
            self._logg_repo.git.checkout(branch)

    def _init_repo(self):
        """ create and initialize a new Git Repo """
        if os.path.exists(self._engine_path):
            log.error("Path already exists! Aborting!")
            raise RuntimeError
        else:
            # create the repo if it doesn't already exist
            _logg_repo = git.Repo.init(path=self._engine_path, mkdir=True)
            record = "idid Logg repo initialized on {0}".format(today())
            c = self._logg_repo.index.commit(record)
            assert c.type == 'commit'
            log.info('Created git repo [{0}]'.format(self._engine_path))
        return _logg_repo

    def _load_repo(self):
        """ Load git repo using GitPython """
        if self._logg_repo:
            return self._logg_repo

        try:
            _logg_repo = git.Repo(self._engine_path)
            log.info('Loaded git repo [{0}]'.format(self._engine_path))
        except Exception:
            # FIXME: should this be automatic?
            # log.error("Git repo doesn't exist! run ``idid init``")
            _logg_repo = self._init_repo()
        return _logg_repo
