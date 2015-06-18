# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs-disable-rg command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..protocol import protocols


@Command.deco(('ccs-disable-rg',
                   ('ccs-version-bump')))
def ccs_disable_rg(cmd_ctxt,
                   input="/etc/cluster/cluster.conf",
                   output="cluster-disabledrg-{ccs-disable-rg.in.hash}.conf",
                   noversionbump=False):
    """Make config. prevent RGManager from (accidentally) starting

    Options:
        input          input CMAN-based cluster configuration file
        output         output file with RGManager being declaratively disabled
        noversionbump  prevent incrementing in-document configuration version
    """
    if noversionbump:
        cmd_ctxt['filter_noop'].append('ccs-version-bump')

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        (
            file_proto(output),
        ),
    )
