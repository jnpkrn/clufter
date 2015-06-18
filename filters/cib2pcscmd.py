# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cib2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter
from ..utils_xml import squote
from ..utils_xslt import xslt_params

TMP_CIB = 'tmp-cib.xml'


@XMLFilter.deco('cib', 'string-list')
def cib2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the cluster per existing CIB"""
    dry_run = flt_ctxt.get('pcscmd_dryrun', False)
    tmp_cib = TMP_CIB if dry_run else flt_ctxt.get('pcscmd_tmpcib', TMP_CIB)
    return (
        'bytestring',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            textmode=True,
            def_first=xslt_params(
                pcscmd_force=flt_ctxt.get('pcscmd_force', False),
                pcscmd_verbose=flt_ctxt.get('pcscmd_verbose', True),
                pcscmd_tmpcib=squote(tmp_cib),
                pcscmd_dryrun=dry_run,
                pcscmd_pcs=squote("pcs -f {0} ".format(tmp_cib)
                                  if tmp_cib else "pcs "),
            ),
        ),
    )
