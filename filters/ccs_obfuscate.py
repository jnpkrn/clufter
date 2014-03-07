# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""obfuscation filters for ccs"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from clufter.filter import XMLFilter
#from lxml import etree


def _ccs_obfuscate(flt_ctxt, in_obj):
    #print etree.tostring(in_obj('etree').xslt(flt.get_template(in_obj)))
    if flt_ctxt['skip']:
        res = in_obj('etree')
    else:
        res = flt_ctxt.proceed_xslt_filter(in_obj)
    return ('etree', res)


@XMLFilter.deco('ccs', 'ccs')
def ccs_obfuscate_credentials(flt_ctxt, in_obj):
    return _ccs_obfuscate(flt_ctxt, in_obj)


@XMLFilter.deco('ccs', 'ccs')
def ccs_obfuscate_identifiers(flt_ctxt, in_obj):
    return _ccs_obfuscate(flt_ctxt, in_obj)
