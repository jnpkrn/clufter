# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs-revitalize command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..protocol import protocols


@Command.deco('ccs-revitalize')
def ccs_revitalize(cmd_ctxt,
                   input="/etc/cluster/cluster.conf",
                   output="./cluster.conf"):
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
