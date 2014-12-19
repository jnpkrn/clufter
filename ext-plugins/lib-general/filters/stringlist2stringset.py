# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""stringlist2stringset filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import Filter

@Filter.deco('string-iter', 'string-set')
def stringlist2stringset(flt_ctxt, in_obj):
    """Downgrades list to a set (order not preserved)"""
    return ('stringset', set(in_obj('stringiter', protect_safe=True)))
