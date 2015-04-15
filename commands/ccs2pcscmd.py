# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2pcscmd{,-flatiron,-needle} commands"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command, CommandAlias
from ..facts import cluster_pcs_flatiron
from ..filter import XMLFilter
from ..protocol import protocols
from ..utils_cman import PATH_CLUSTERCONF
from .ccs2pcs import ccsflat2cibfinal_chain


@Command.deco(('ccs2ccsflat',
                  ('ccs2ccs-pcmk',
                      ('ccspcmk2pcscmd',
                          ('stringiter-combine2'))),
                  (ccsflat2cibfinal_chain,
                      ('cib2pcscmd',
                          ('stringiter-combine2')))))
def ccs2pcscmd_flatiron(cmd_ctxt,
                        input=PATH_CLUSTERCONF,
                        output="-",
                        _common=XMLFilter.command_common):
    """(CMAN,rgmanager) cluster cfg. -> equivalent in pcs commands

    Options:
        input     input (CMAN,rgmanager) cluster config. file
        output    pcs commands to reinstate the cluster per the inputs
    """

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        (
            (
                (
                    file_proto(output),
                ),
            ),
            #(
            #    (
            #        (
            #            (
            #                (
            #                    (
            #                        file_proto(output),  # already tracked
            #                    ),
            #                ),
            #            ),
            #        ),
            #    ),
            #),
        ),
    )


@Command.deco(('ccs2ccsflat',
                  ('ccs-propagate-cman',
                      ('ccs2needlexml',
                          ('needlexml2pcscmd',
                              ('stringiter-combine2')))),
                  (ccsflat2cibfinal_chain,
                      ('cib2pcscmd',
                          ('stringiter-combine2')))))
def ccs2pcscmd_needle(cmd_ctxt,
                      input=PATH_CLUSTERCONF,
                      output="-",
                      _common=XMLFilter.command_common):
    """[COMMAND CURRENTLY UNAVAILABLE]

    Options:
        input     input (CMAN,rgmanager) cluster configuration file
        output    pcs commands to reinstate the cluster per the inputs
    """
    #"""(CMAN,rgmanager) cluster cfg. -> equivalent in pcs commands
    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        (
            (
                (
                    (
                        file_proto(output),
                    ),
                ),
            ),
            #(
            #    (
            #        (
            #            (
            #                (
            #                    (
            #                        file_proto(output),  # already tracked
            #                    ),
            #                ),
            #            ),
            #        ),
            #    ),
            #),
        ),
    )


@CommandAlias.deco
def ccs2pcscmd(cmds, *sys_id):
    # cluster_pcs_needle assumed unless "cluster_pcs_flatiron"
    return (ccs2pcscmd_flatiron if cluster_pcs_flatiron(*sys_id) else
            ccs2pcscmd_needle)
