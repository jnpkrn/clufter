# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Various helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os
import sys
from optparse import make_option
from subprocess import Popen

from .error import ClufterError


def selfaware(func):
    """Decorator suitable for recursive staticmethod"""
    def selfaware_inner(*args, **kwargs):
        return func(selfaware(func), *args, **kwargs)
    map(lambda a: setattr(selfaware_inner, a, getattr(func, a)),
        ('__doc__', '__name__'))
    return selfaware_inner

# inspired by http://stackoverflow.com/a/4374075
mutable = lambda x: isinstance(x, (basestring, int, long, bool, float, tuple))

tuplist = lambda x: isinstance(x, (tuple, list))
# turn args into tuple unless single tuplist arg
args2sgpl = \
    lambda x=(), *y: x if not y and tuplist(x) else (x, ) + y
# turn args into tuple unconditionally
args2tuple = lambda *args: tuple(args)
any2iter = \
    lambda x: \
        x if hasattr(x, 'next') and hasattr(x.next, '__call__') \
        else iter(args2sgpl(x, None))

head_tail = \
    lambda x=None, *y, **kwargs: \
        (x, args2sgpl(*y)) if not tuplist(x) or kwargs.get('stop', 0) \
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
            type(item)(apply_preserving_depth(action)(i) for i in item) \
            if tuplist(item) else action(item)
apply_aggregation_preserving_depth = \
    lambda agg_fn: \
        lambda item: \
            agg_fn(type(item)(apply_aggregation_preserving_depth(agg_fn)(i)
                              for i in item)) \
            if tuplist(item) else item
apply_aggregation_preserving_passing_depth = \
    lambda agg_fn, d=0: \
        lambda item: \
            agg_fn(type(item)(
                apply_aggregation_preserving_passing_depth(agg_fn, d+1)(i)
                for i in item),
                d+1
            ) \
            if tuplist(item) else item
# name comes from Haskell
# note: always returns list even for input tuple
# note: when returning from recursion, should always observe scalar or list(?)
apply_intercalate = apply_aggregation_preserving_depth(
    lambda i:
        reduce(lambda a, b: a + (b if isinstance(b, list) else [b]),
               i, [])
)

bifilter = \
    lambda fnc, seq: \
        reduce(lambda acc, x: acc[int(not fnc(x))].append(x) or acc,
               seq, ([], []))

# Given the partitioning function, do the recursive refinement in a way
# the parts reaching the bottom line in more steps are continually "shaked"
# towards the end (with stable the relative order, though).
# Default partitioning function just distinguishes between tuples/lists
# and other values (presumably scalars) so when passed a tuple/list encoding
# a graph (tree/forest) in a DFS manner using unrestricted nesting, it will
# return serialized BFS walk of the same.
# NOTE if there are scalars already at the start-level depth, use
#      `tail_shake_safe` (not that it provides much more guarantee :-p)
tailshake = \
    lambda src, partitioner=(lambda x: not tuplist(x)): \
        reduce(lambda a, b: a + (tailshake(b, partitioner) if b else b),
               reduce(lambda a, b: (a[0] + b[0], a[1] + b[1]),
                      tuple(bifilter(partitioner, i) if tuplist(i) else (i, [])
                      for i in src), ([], [])))

tailshake_safe = \
    lambda src, partitioner=(lambda x: not tuplist(x)): \
        tailshake(src if all(tuplist(i) for i in src) else (src, ),
                  partitioner)


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

# prioritize consonants, deprioritize vowels (except for the first letter
# overall), which seems to be widely adopted technique for selecting short
# options based on their long counterparts :)
longopt_letters_reprio = \
    lambda longopt: \
        longopt[0] + ''.join(sorted(longopt[1:],
                                    key=lambda x: int(x.lower() in 'aeiouy')))

# extrapolate optparse.make_option to specifically-encoded "plural"
make_options = lambda opt_decl: [make_option(*a, **kw) for a, kw in opt_decl]

def func_defaults_varnames(func, skip=0):
    """Using introspection, get arg defaults (dict) + all arg names (tuple)

    Parameters:
        skipfirst   how many initial arguments to skip
    """
    # XXX assert len(func_varnames) - skip >= len(func.func_defaults)
    func_varnames = func.func_code.co_varnames[skip:]
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
