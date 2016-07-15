# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""stringiter-combine filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from itertools import chain

from ..filter import Filter


def stringiter_combine(flt_ctxt, in_objs):
    """Combine multiple string-iter objects"""
    return ('stringiter',
            chain(*tuple(o('stringiter', protect_safe=True) for o in in_objs)))

@Filter.deco(('string-iter', ) * 2, 'string-iter')
def stringiter_combine2(flt_ctxt, in_objs):
    return stringiter_combine(flt_ctxt, in_objs)

@Filter.deco(('string-iter', ) * 3, 'string-iter')
def stringiter_combine3(flt_ctxt, in_objs):
    return stringiter_combine(flt_ctxt, in_objs)

# ...
