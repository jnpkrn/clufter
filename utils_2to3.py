# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Python 2-to-3 porting stuff (helpers, etc.)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from collections import deque
from functools import reduce
from sys import modules, version_info


PY3 = version_info[0] >= 3


# Compatibility import chains (respective symbols to be used via this module)

try:
    StandardError = StandardError
except NameError:
    StandardError = Exception

try:
    basestring = basestring
except NameError:
    basestring = str

try:
    xrange = xrange
except NameError:
    xrange = range


# Compatibility with dictionary methods not present in Python 3

# See https://www.python.org/dev/peps/pep-0469/#id9
try:
    dict.iteritems
except AttributeError:  # Python 3
    iter_values = lambda d: iter(d.values())
    iter_items = lambda d: iter(d.items())
else:  # Python 2
    iter_values = lambda d: d.itervalues()
    iter_items = lambda d: d.iteritems()


# Compatibility with implicit arguments unpacking not present in Python 3

# We were using implicit arguments unpacking heavily upon composite iterated
# elements coming as a second part of the `enumerate` product, especially in
# terse expressions using lambdas.  Python 3 does not allow this anymore,
# so we resort to using custom version of `enumerate` that will unpack the
# arguments for us.
# Similarly for: filter, map, reduce (incl. double nesting), and artificial
#                foreach function newly introduced in utils_func
enumerate_u = \
    lambda *seq_start: \
        ((lambda *a: a)(i, *item) for i, item in enumerate(*seq_start))

filter_u = lambda func, iterable: filter(lambda i: func(*i), iterable)
map_u = lambda func, *iterables: map(lambda i: func(*i), *iterables)
reduce_u = \
    lambda func, *sequence_initial: \
        reduce(lambda acc, new: func(acc, *new), *sequence_initial)
# double unpack, expects sequence of pairs of pairs
reduce_uu = \
    lambda func, *sequence_initial: \
        reduce(lambda acc, new: func(
            *(reduce(lambda a, rest: a + list(rest), (acc, new), []))
        ),*sequence_initial)

foreach_u = lambda *args: deque(map_u(*args), maxlen=0)


# Compatibility with different way to use metaclasses in Python 2/3

class MimicMeta(object):
    """

    https://www.python.org/dev/peps/pep-3115/
    https://wiki.python.org/moin/PortingToPy3k/BilingualQuickRef#metaclasses
    """
    _sm = staticmethod  # workaround the identifiers-in-scope clash (deco)
    @_sm
    def method(m):
        setattr(m, '__mimicmeta__', None)
        return staticmethod(m)
    @_sm
    def staticmethod(m):
        setattr(m, '__mimicmeta__', staticmethod)
        return staticmethod(m)
    @_sm
    def classmethod(m):
        setattr(m, '__mimicmeta__', classmethod)
        return staticmethod(m)
    @_sm
    def passdeco(d):
        def _passdeco(m):
            setattr(m, '__mimicmeta__', d)
            return staticmethod(m)
        return _passdeco

    def __new__(cls, name, metaclass, deriveclass, bases=()):
        attrs = dict(__doc__=deriveclass.__doc__, __metaclass__=metaclass)
        for n in dir(deriveclass):
            attr = getattr(deriveclass, n)
            try:
                wrapper = attr.__mimicmeta__ or (lambda x: x)
                attrs.setdefault(n, wrapper(attr))
            except AttributeError:
                pass
        return metaclass(str(name), bases, attrs)
