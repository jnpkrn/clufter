# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs_obfuscate_credentials filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from clufter.filter import XMLFilter
#from lxml import etree


@XMLFilter.deco('ccs', 'ccs')
def ccs_obfuscate_credentials(flt_ctxt, in_obj):
    #print etree.tostring(in_obj('etree').xslt(flt.get_template(in_obj)))
    res = flt_ctxt.proceed_xslt_filter(in_obj, symbol='obfuscate_credentials')
    return ('etree', res)
