# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccspcmk2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter
from ..utils_xml import squote
from ..utils_xslt import xslt_boolean, xslt_params


@XMLFilter.deco('ccs', 'string-list')
def ccspcmk2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the cluster per cluster.conf"""
    return (
        'bytestring',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            textmode=True,
            def_first=xslt_params(
                pcscmd_force=xslt_boolean(flt_ctxt.get('pcscmd_force', 0)),
                pcscmd_noauth=xslt_boolean(flt_ctxt.get('pcscmd_noauth', 0)),
                pcscmd_verbose=xslt_boolean(flt_ctxt.get('pcscmd_verbose', 1)),
                pcscmd_dryrun=xslt_boolean(flt_ctxt.get('pcscmd_dryrun', 0)),
            ),
        ),
    )
