# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2coro filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from clufter.filter import XMLFilter
#from lxml import etree


def _ccs2coroxml(flt_ctxt, in_obj):
    #print etree.tostring(in_obj('etree').xslt(flt.get_template(in_obj)))
    return ('etree', flt_ctxt.proceed_xslt(in_obj))

@XMLFilter.deco('ccs', 'coroxml')
def ccs2flatironxml(flt_ctxt, in_obj):
    return _ccs2coroxml(flt_ctxt, in_obj)

@XMLFilter.deco('ccs', 'coroxml')
def ccs2needlexml(flt_ctxt, in_obj):
    return _ccs2coroxml(flt_ctxt, in_obj)
