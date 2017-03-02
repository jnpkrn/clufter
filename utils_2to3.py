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
