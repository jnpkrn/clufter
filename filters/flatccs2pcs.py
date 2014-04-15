# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""flatccs2pcs filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from clufter.filter import XMLFilter


@XMLFilter.deco('flatccs', 'pcs')
def flatccs2pcs(flt_ctxt, in_obj):
    return ('etree', flt_ctxt.proceed_xslt_filter(in_obj))
