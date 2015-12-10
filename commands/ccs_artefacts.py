# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs-artefacts command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..protocol import protocols
from ..utils_cman import PATH_CLUSTERCONF


@Command.deco('ccs-artefacts')
def ccs_artefacts(cmd_ctxt,
                  input=PATH_CLUSTERCONF,
                  output="cman-artefacts-{ccs-artefacts.in.hash}.conf"):
    """Output artefacts referenced in the config. in CVS format

    Options:
        input   input CMAN-based cluster configuration file
        output  output file with collected artefacts (files, etc.)
    """

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        file_proto(output),
    )
