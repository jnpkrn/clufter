# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccspcmk2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter
from ..utils_xslt import xslt_params


@XMLFilter.deco('ccs', 'string-list')
def ccspcmk2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the cluster per cluster.conf"""
    return (
        'bytestring',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            textmode=True,
            def_first=xslt_params(
                pcscmd_force=flt_ctxt.get('pcscmd_force', False),
                pcscmd_noauth=flt_ctxt.get('pcscmd_noauth', False),
                pcscmd_verbose=flt_ctxt.get('pcscmd_verbose', True),
                pcscmd_dryrun=flt_ctxt.get('pcscmd_dryrun', False),
                pcscmd_enable=flt_ctxt.get('pcscmd_enable', False),
                pcscmd_start_wait=flt_ctxt.get('pcscmd_start_wait', 90),
                pcscmd_noguidance=flt_ctxt.get('pcscmd_noguidance', False),
            ),
        ),
    )
