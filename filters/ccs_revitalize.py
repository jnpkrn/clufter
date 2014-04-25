# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs_revitalize filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from clufter.filter import XMLFilter


@XMLFilter.deco('ccs', 'ccs')
def ccs_revitalize(flt_ctxt, in_obj):
    return ('etree', flt_ctxt.proceed_xslt_filter(in_obj))
