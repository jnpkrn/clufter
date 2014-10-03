# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Program-specific commons"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from collections import Mapping, MutableMapping, MutableSequence, MutableSet
from optparse import make_option
from os import environ, pathsep
from os.path import abspath, dirname, samefile, \
                    isabs as path_isabs, \
                    isfile as path_isfile, \
                    join as path_join
from subprocess import Popen
from sys import stderr, stdin

from . import package_name
from .error import ClufterError
from .utils import areinstances, \
                   filterdict_pop, \
                   func_defaults_varnames, \
                   isinstanceexcept, \
                   selfaware, \
                   tuplist


#
# generics
#

mutables = (MutableMapping, MutableSequence, MutableSet)

class TweakedDict(MutableMapping):
    """Object representing command context"""

    class notaint_context(object):
        def __init__(self, self_outer, exit_off):
            self._exit_off = exit_off
            self._self_outer = self_outer
        def __enter__(self):
            self._exit_off |= not self._self_outer._notaint
            self._self_outer._notaint = True
        def __exit__(self, *exc):
            self._self_outer._notaint = not self._exit_off

    def __init__(self, initial=None, bypass=False, notaint=False):
        self._parent = self
        self._notaint = True
        if areinstances(initial, self):
            assert initial._parent is initial
            self._dict = initial._dict  # trust dict to have expected props
            notaint = initial._notaint
        else:
            self._dict = {}
            if initial is not None:
                if not isinstance(initial, Mapping):
                    initial = dict(initial)
                elif not isinstance(initial, MutableMapping):
                    # silently? follow the immutability
                    notaint = True
                    bypass = True
                if bypass or notaint:
                    self._dict = initial
                if not bypass:
                    # full examination
                    self._notaint = False  # temporarily need to to allow
                    map(lambda (k, v): self.__setitem__(k, v),
                                       initial.iteritems())
        self._notaint = notaint

    def __delitem__(self, key):
        if any(getattr(p, '_notaint', False) for p in self.anabasis):
            raise RuntimeError("Cannot del item in notaint context")
        del self._dict[key]

    def __getitem__(self, key):
        # any notainting parent incl. self is an authority for us
        try:
            ret = self._dict[key]
        except KeyError:
            if self._parent is self:
                raise
            ret = self._parent[key]
        if (isinstanceexcept(ret, mutables, TweakedDict)
            and any(getattr(p, '_notaint', False) for p in self.anabasis)):
            ret = ret.copy()
        return ret

    @property
    def anabasis(self):
        """Traverse nested contexts hierarchy upwards"""
        return (self, )

    def setdefault(self, key, *args, **kwargs):
        """Allows implicit arrangements to be bypassed via `bypass` flag"""
        assert len(args) < 2
        bypass = kwargs.get('bypass', False)
        if bypass:  # for when adding MutableMapping that should be untouched
            return self._dict.setdefault(key, *args)
        try:
            return self.__getitem__(key)
        except KeyError:
            if not args:
                raise
            self.__setitem__(key, *args)
            return args[0]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return "<{0}: {1}>".format(repr(self.__class__), repr(self._dict))

    def __setitem__(self, key, value):
        # XXX value could be also any valid dict constructor argument
        if any(getattr(p, '_notaint', False) for p in self.anabasis):
            raise RuntimeError("Cannot set item in notaint context")
        self._dict[key] = value

    def prevented_taint(self, exit_off=False):
        """Context manager to safely yield underlying dicts while applied"""
        return self.notaint_context(self, exit_off)

ProtectedDict = lambda track: TweakedDict(track, notaint=True, bypass=True)


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
        where, expand_path = [''], False
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
    """Use when you have a func with common initial kwargs consumption

    Calling this on another function will, upon invocation, first look
    at default argument to `_common` keyword parameter, and if present,
    will consider it as a function to be run before the one passed as
    an argument; aside from returning a function decorated in a stated
    way, it will also return dict of function paramater defaults (joint
    for both original and '_common' function) and a list of joint
    function arguments.

    In other words, it allows DRY principle for common shared initial
    kwargs "consumer" function on top of (actually prior to) the function
    being passed in as an argument.
    """
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


def getenv_namespaced(varname, value=None, namespace=package_name().upper()):
    """Obtain value of environment variable prefixed with `namespace + '_'`"""
    return environ.get('_'.join((namespace, varname)), value)
