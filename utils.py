# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Various helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os
import sys
from subprocess import Popen


# name the exitcodes
ecodes = 'SUCCESS', 'FAILURE'
EC = type('EC', (), dict((n, v) for v, n
                         in enumerate('EXIT_' + i for i in ecodes)))


head_tail = lambda x=None, *y: (x, x if x is None else y)
filtervars = lambda src, which: \
             dict((x, src[x]) for x in which if x in src)
filtervarsdef = lambda src, which: \
                dict((x, src[x]) for x in which if src.get(x, None))
filtervarspop = lambda src, which: \
                dict((x, src.pop(x)) for x in which if x in src)
apply_preserving_depth = \
    lambda action: \
        lambda item: \
            type(item)([apply_preserving_depth(action)(i) for i in item]) \
            if isinstance(item, (tuple, list)) else action(item)
apply_aggregation_preserving_depth = \
    lambda agg_fn: \
        lambda item: \
            agg_fn([apply_aggregation_preserving_depth(agg_fn)(i)
                    for i in item]) \
            if isinstance(item, (tuple, list)) else item
# name comes from Haskell
# note: always returns list even for input tuple
# note: when returning from recursion, should always observe scalar or list(?)
apply_intercalate = apply_aggregation_preserving_depth(
    lambda i:
        reduce(lambda a, b: a + (b if isinstance(b, list) else [b]),
               i, [])
)


def which(name, *where):
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


class ClufterError(Exception):
    def __init__(self, ctx_self, msg, *args):
        self.ctx_self = ctx_self
        self.msg = msg

    def __str__(self):
        ret = getattr(self.ctx_self, '__name__',
                      self.ctx_self.__class__.__name__)
        return ret + ': ' + self.msg.format(*self.args)


class ClufterPlainError(ClufterError):
    def __init__(self, msg, *args):
        super(ClufterPlainError, self).__init__(self, None, msg, *args)


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
