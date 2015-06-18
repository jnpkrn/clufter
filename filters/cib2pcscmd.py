# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cib2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter
from ..utils_xml import squote
from ..utils_xslt import xslt_params


@XMLFilter.deco('cib', 'string-list', defs=dict(
    pcscmd_force=False,
    pcscmd_verbose=True,
    pcscmd_tmpcib='tmp-cib.xml',
    pcscmd_dryrun=False,
))
def cib2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the cluster per existing CIB"""
    self = flt_ctxt.ctxt_wrapped
    dry_run, tmp_cib = flt_ctxt['pcscmd_dryrun'], flt_ctxt['pcscmd_tmpcib']
    tmp_cib = (tmp_cib or self.defs['pcscmd_tmpcib']) if dry_run else tmp_cib
    return (
        'bytestring',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            textmode=True,
            def_first=xslt_params(
                pcscmd_force=flt_ctxt['pcscmd_force'],
                pcscmd_verbose=flt_ctxt['pcscmd_verbose'],
                pcscmd_tmpcib=squote(flt_ctxt['pcscmd_tmpcib']),
                pcscmd_dryrun=dry_run,
                pcscmd_pcs=squote("pcs -f {0} ".format(tmp_cib)
                                  if tmp_cib else "pcs "),
            ),
        ),
    )
