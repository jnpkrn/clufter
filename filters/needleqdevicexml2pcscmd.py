# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""needleqdevicexml2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..facts import infer
from ..filter import XMLFilter
from ..utils_xslt import xslt_params


@XMLFilter.deco('coroxml-needle', 'string-list', defs=dict(
    pcscmd_force=False,
    pcscmd_verbose=True,
    pcscmd_noguidance=0,
))
def needleqdevicexml2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the qdevice per corosync.conf"""
    return (
        'bytestring',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            textmode=True,
            def_first=xslt_params(
                pcscmd_force=flt_ctxt['pcscmd_force'],
                pcscmd_verbose=flt_ctxt['pcscmd_verbose'],
                pcscmd_noguidance=flt_ctxt['pcscmd_noguidance'],

                pcscmd_extra_qdevice = bool(infer(
                    'comp:corosync[qdevice] + comp:pcs[qdevice]',
                    flt_ctxt['system'],
                    flt_ctxt['system_extra'],
                )),
                pcscmd_extra_qdevice_heuristics = bool(infer(
                    'comp:corosync[qdevice-heuristics] + comp:pcs[qdevice-heuristics]',
                    flt_ctxt['system'],
                    flt_ctxt['system_extra'],
                )),
                pcscmd_extra_qnet = bool(infer(
                    'comp:corosync[qnet] + comp:pcs[qnet]',
                    flt_ctxt['system'],
                    flt_ctxt['system_extra'],
                )),
            ),
        ),
    )
