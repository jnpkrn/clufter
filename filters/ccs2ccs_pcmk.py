# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2ccs_pcmk filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter


@XMLFilter.deco('ccs', 'ccs')
def ccs2ccs_pcmk(flt_ctxt, in_obj):
    # could be static output, but stay with XSLT in case we want to move sth.
    # from cluster.conf to corosync.conf already (used to be a case);
    # there is also a possibility to put service-only directive
    # as a file under /etc/corosync/service.d/ (called, e.g., pcmk,
    # see Clusters from Scratch document)
    return ('etree', flt_ctxt.ctxt_proceed_xslt(in_obj))
