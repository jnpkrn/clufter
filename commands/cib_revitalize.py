# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cib-revitalize command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..protocol import protocols
from ..utils_cib import PATH_CIB


@Command.deco('cib-revitalize')
def cib_revitalize(cmd_ctxt,
                   input=PATH_CIB,
                   output="cib-revitalized-{cib-revitalize.in.hash}.xml"):
    """Migrate deprecated configuration items in CIB

    Options:
        input   input proper Pacemaker cluster configuration file (CIB)
        output  output file with "revitalized" content
    """
    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        file_proto(output),
    )
