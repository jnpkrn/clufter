# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2ccs_pcmk filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from clufter.filter import XMLFilter
#from lxml import etree


@XMLFilter.deco('ccs', 'ccs')
def ccs2ccs_pcmk(flt_ctxt, in_obj):
    return ('etree', flt_ctxt.proceed_xslt(in_obj))
