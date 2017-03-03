# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Python 2-to-3 porting stuff (helpers, etc.)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

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
