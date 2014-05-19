# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Program-specific commons"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from optparse import make_option
from os import environ, path, pathsep
from subprocess import Popen
from sys import stderr, stdin

from .error import ClufterError


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
        (lambda lo: \
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
      and (path.samefile(opts.logfile, last_hdlr.baseFilename)
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

def which(name, *where):
    """Mimic `which' UNIX utility"""
    where = tuple(path.abspath(i) for i in where)
    if 'PATH' in environ:
        use_path = tuple(i for i in environ['PATH'].split(pathsep)
                         if len(i.strip()))
    else:
        use_path = ()
    for p in where + use_path:
        check = path.join(p, name)
        if path.exists(check):
            return check
    else:
        return None
