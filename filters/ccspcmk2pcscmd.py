# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccspcmk2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter


@XMLFilter.deco('ccs', 'string-list')
def ccspcmk2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the cluster per cluster.conf"""
    return ('bytestring', flt_ctxt.ctxt_proceed_xslt(in_obj, textmode=True))
