# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Various helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os
import sys
from subprocess import Popen

from .error import ClufterError


tuplist = lambda x: isinstance(x, (tuple, list))
# turn args into tuple unless single tuplist arg
args2sgpl = \
    lambda x=(), *y: x if not y and tuplist(x) else (x, ) + y
# turn args into tuple unconditionally
args2tuple = lambda *args: tuple(args)
head_tail = \
    lambda x=None, *y, **kwargs: \
        (x, args2sgpl(*y)) if not tuplist(x)  or kwargs.get('stop', 0) \
                           else (head_tail(stop=1, *tuple(x) + y))

filtervars = \
    lambda src, which: dict((x, src[x]) for x in which if x in src)
filtervarsdef = \
    lambda src, which: dict((x, src[x]) for x in which if src.get(x, None))
filtervarspop = \
    lambda src, which: dict((x, src.pop(x)) for x in which if x in src)
apply_preserving_depth = \
    lambda action: \
        lambda item: \
            type(item)([apply_preserving_depth(action)(i) for i in item]) \
            if tuplist(item) else action(item)
apply_aggregation_preserving_depth = \
    lambda agg_fn: \
        lambda item: \
            agg_fn([apply_aggregation_preserving_depth(agg_fn)(i)
                    for i in item]) \
            if tuplist(item) else item
apply_aggregation_preserving_passing_depth = \
    lambda agg_fn, d=0: \
        lambda item: \
            agg_fn([apply_aggregation_preserving_passing_depth(agg_fn, d+1)(i)
                    for i in item], d+1) \
            if tuplist(item) else item
# name comes from Haskell
# note: always returns list even for input tuple
# note: when returning from recursion, should always observe scalar or list(?)
apply_intercalate = apply_aggregation_preserving_depth(
    lambda i:
        reduce(lambda a, b: a + (b if isinstance(b, list) else [b]),
               i, [])
)

zipped_outlier = type('zipped_outlier', (tuple, ), {})
zip_empty = type('zip_filler', (str, ), {})("EMPTY")
loose_zip = lambda a, b: zip(
    list(a) + (max(len(a), len(b)) - len(a)) * [zip_empty],
    list(b) + (max(len(a), len(b)) - len(b)) * [zip_empty]
)
apply_loose_zip_preserving_depth = \
    lambda a, b: \
        (type(a) if type(a) == type(b) else type(a))(
            [apply_loose_zip_preserving_depth(*p) for p in loose_zip(a, b)]
        ) if tuplist(a) == tuplist(b) == True else zipped_outlier([a, b])
# as previous, but with length checking of some sort
# NOTE: automatically shortens the longer counterpart in the pair
#       to the length of the bigger one
apply_strict_zip_preserving_depth = \
    lambda a, b: \
        (type(a) if type(a) == type(b) else type(a))(
            [apply_strict_zip_preserving_depth(*p) for p in zip(a, b)]
        ) if tuplist(a) == tuplist(b) == True and len(a) == len(b) \
        else zipped_outlier([a, b])


def which(name, *where):
    """Mimic `which' UNIX utility"""
    where = tuple(os.path.abspath(i) for i in where)
    if 'PATH' in os.environ:
        path = tuple(i for i in os.environ['PATH'].split(os.pathsep)
                     if len(i.strip()))
    else:
        path = ()
    for p in where + path:
        check = os.path.join(p, name)
        if os.path.exists(check):
            return check
    else:
        return None


def func_defaults_varnames(func):
    """Using introspection, get a dict of kwargs' defaults + all arg names"""
    func_varnames = func.func_code.co_varnames
    func_defaults = dict(zip(
        func_varnames[-len(func.func_defaults):],
        func.func_defaults
    ))
    return func_defaults, func_varnames


class OneoffWrappedStdinPopen(object):
    """Singleton to watch for atmost one use of stdin in Popen context"""
    def __init__(self):
        self._used = False

    def __call__(self, args, **kwargs):
        if not 'stdin' in kwargs and '-' in args:
            if self._used:
                raise ClufterError(self, 'repeated use detected')
            kwargs['stdin'] = sys.stdin
            # only the first '-' substituted
            args[args.index('-')] = '/dev/stdin'
            self._used |= True
        return Popen(args, **kwargs)

OneoffWrappedStdinPopen = OneoffWrappedStdinPopen()


# Inspired by http://stackoverflow.com/a/1383402
class classproperty(property):
    def __init__(self, fnc):
        property.__init__(self, classmethod(fnc))

    def __get__(self, this, owner):
        return self.fget.__get__(None, owner)()


class hybridproperty(property):
    def __init__(self, fnc):
        property.__init__(self, classmethod(fnc))

    def __get__(self, this, owner):
        return self.fget.__get__(None, this if this else owner)()
