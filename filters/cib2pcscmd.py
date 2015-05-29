# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cib2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter
from ..utils_xml import squote
from ..utils_xslt import xslt_boolean, xslt_params


@XMLFilter.deco('cib', 'string-list')
def cib2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the cluster per existing CIB"""
    tmp_cib = flt_ctxt.get('pcscmd_tmpcib', 'tmp-cib.xml')
    return (
        'bytestring',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            textmode=True,
            def_first=xslt_params(
                pcscmd_verbose=xslt_boolean(flt_ctxt.get('pcscmd_verbose', 1)),
                pcscmd_tmpcib=squote(tmp_cib),
                pcscmd_pcs=squote("pcs -f {0} ".format(tmp_cib)
                                  if tmp_cib else "pcs "),
            ),
        ),
    )
