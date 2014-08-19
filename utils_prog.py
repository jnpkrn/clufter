# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Program-specific commons"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from optparse import make_option
from os import environ, pathsep
from os.path import abspath, dirname, samefile, \
                    isabs as path_isabs, \
                    isfile as path_isfile, \
                    join as path_join
from subprocess import Popen
from sys import stderr, stdin

from .error import ClufterError
from .utils import filterdict_pop, func_defaults_varnames, selfaware, tuplist


#
# command-line options related
#

# dashes recommended by 5 of 4 terminal fanboys
# NB underscores -> dashes swap is idempotent in regards to the member
#    name of where optparse stores respective option value, but here
#    the list of possible operations to preserve such property stops!
#    + also to preserve reversibility/bijection, original ought to be
#      free of the substituting character
cli_decor = lambda x: x.replace('_', '-')
cli_undecor = lambda x: x.replace('-', '_')

# prioritize consonants, deprioritize vowels (except for the first letter
# overall), which seems to be widely adopted technique for selecting short
# options based on their long counterparts ;)
# XXX could eventually also resort to using upper-case chars
longopt_letters_reprio = \
    lambda longopt: \
        (lambda lo:
            lo[0] + ''.join(sorted(lo[1:],
                                   key=lambda x: int(x.lower() in 'aeiouy')))
        )(filter(lambda c: c.isalpha(), longopt))

# extrapolate optparse.make_option to specifically-encoded "plural"
make_options = lambda opt_decl: [make_option(*a, **kw) for a, kw in opt_decl]


def set_logging(opts):
    """Apply logging options as per `opts' to the live logging configuration"""
    rootlog = logging.getLogger()
    last_hdlr = rootlog.handlers.pop()
    if isinstance(last_hdlr, logging.FileHandler if opts.logfile
                             else logging.StreamHandler) \
      and (samefile(opts.logfile, last_hdlr.baseFilename)
           if opts.logfile else last_hdlr.stream is stderr):
        hdlr = last_hdlr
    else:
        hdlr = logging.FileHandler(opts.logfile) if opts.logfile \
               else logging.StreamHandler()
        hdlr.setFormatter(last_hdlr.formatter)
    rootlog.addHandler(hdlr)
    rootlog.setLevel(logging.getLevelName(opts.loglevel))


class OneoffWrappedStdinPopen(object):
    """Singleton to watch for atmost one use of stdin in Popen context"""
    def __init__(self):
        self._used = False

    def __call__(self, args, **kwargs):
        if not 'stdin' in kwargs and '-' in args:
            if self._used:
                raise ClufterError(self, 'repeated use detected')
            kwargs['stdin'] = stdin
            # only the first '-' substituted
            args[args.index('-')] = '/dev/stdin'
            self._used |= True
        return Popen(args, **kwargs)

OneoffWrappedStdinPopen = OneoffWrappedStdinPopen()


#
# misc
#

def which(name, single='', *paths, **redefine_check):
    """Mimic `which' UNIX utility

    Both `single` and `paths` denotes paths to be tried for `name` lookup,
    which includes a decision from the perspective of a filter function given
    by `check` keyword argument (default: a test if the file exists at all).

    What is special about `single` is that it can be defined as either
    plain one-path string, PATH-like-separated list of paths, or
    an iterable.  It is decomposed into a list of paths and then
    `paths` items appended.

    Apparently, when `name` is provided as an absolute path, only
    the `check` (i.e., no lookup) phase is performed.

    If nothing matching the criteria is found, `None` is returned,
    nominal path as per `name` (and `check` for that matter) otherwise.

    Empty string instructs code to use environment's PATH instead.
    """
    check, expand_path = redefine_check.pop('check', path_isfile), True
    if path_isabs(name):
        where, expand_path = ['', ], False
    else:
        where = list(single.split(pathsep) if not tuplist(single) else single)
        where.extend(paths)
        where.reverse()
    while where:
        p = where.pop()
        if not p:
            if expand_path:
                where.extend(reversed(environ.get('PATH', '').split(pathsep)))
                expand_path = False
                continue
            elif where:
                break  # degenerated case: multiple ''
        p = path_join(abspath(p), name)
        if check(p):
            return p
    else:
        return None


dirname_x = lambda p, c=1: reduce(lambda x, y: dirname(x), xrange(c), p)


@selfaware
def defer_common(me, fnc, skip=0):
    """Use when you have a func with common initial kwargs consumption"""
    fnc_defaults, fnc_varnames = func_defaults_varnames(fnc, skip=skip)
    common = fnc_defaults.pop('_common', None)
    if not common:
        wrapfnc = fnc
    else:
        common_defaults, common_varnames, common = me(common, skip=skip)
        fnc_defaults.update(common_defaults)
        fnc_varnames = list(fnc_varnames)
        fnc_varnames.remove('_common')  # but we could rely on last argument
        fnc_varnames = tuple(fnc_varnames) + common_varnames

        def wrapfnc(cmd_ctxt, **kwargs):
            common(cmd_ctxt, **filterdict_pop(kwargs, *common_varnames))
            kwargs.pop('_common', None)
            return fnc(cmd_ctxt, **kwargs)
        wrapfnc.__doc__ = fnc.__doc__ + common.__doc__
    return fnc_defaults, fnc_varnames, wrapfnc
