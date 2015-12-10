# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs-revitalize command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..protocol import protocols
from ..utils_cman import PATH_CLUSTERCONF


@Command.deco('ccs-revitalize')
def ccs_revitalize(cmd_ctxt,
                   input=PATH_CLUSTERCONF,
                   output="cluster-revitalized-{ccs-revitalize.in.hash}.conf"):
    """Migrate deprecated config's props (agent params, etc.)

    Options:
        input   input CMAN-based cluster configuration file
        output  output file with "revitalized" content
    """
    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        file_proto(output),
    )
