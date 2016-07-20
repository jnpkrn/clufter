# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""needlexml2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..facts import infer
from ..filter import XMLFilter
from ..utils_xslt import xslt_params


@XMLFilter.deco('coroxml-needle', 'string-list', defs=dict(
    pcscmd_force=False,
    pcscmd_noauth=False,
    pcscmd_verbose=True,
    pcscmd_dryrun=False,
    pcscmd_enable=False,
    pcscmd_start_wait=60,
    pcscmd_noguidance=0,
))
def needlexml2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the cluster per corosync.conf"""
    return (
        'bytestring',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            textmode=True,
            def_first=xslt_params(
                pcscmd_force=flt_ctxt['pcscmd_force'],
                pcscmd_noauth=flt_ctxt['pcscmd_noauth'],
                pcscmd_verbose=flt_ctxt['pcscmd_verbose'],
                pcscmd_dryrun=flt_ctxt['pcscmd_dryrun'],
                pcscmd_enable=flt_ctxt['pcscmd_enable'],
                pcscmd_start_wait=flt_ctxt['pcscmd_start_wait'],
                pcscmd_noguidance=flt_ctxt['pcscmd_noguidance'],

                pcscmd_extra_wait_cluster_start = bool(infer(
                    'comp:pcs[wait-cluster-start]',
                    flt_ctxt['system'],
                    flt_ctxt['system_extra'],
                )),
            ),
        ),
    )
