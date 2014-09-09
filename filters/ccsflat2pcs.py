# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccsflat2pcs filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter


@XMLFilter.deco('ccs', 'pcs')
def ccsflat2pcs(flt_ctxt, in_obj):
    # XXX temporary hack with plain ccs;
    # check that it is indeed ccs-flat, by exploring flt_ctxt?
    return ('etree', flt_ctxt.ctxt_proceed_xslt(in_obj))
