# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""pcs2pcscmd{,-flatiron,-needle} commands"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command, CommandAlias
from ..facts import cluster_pcs_flatiron
from ..filter import XMLFilter
from ..protocol import protocols
from ..utils_cib import PATH_CIB
from ..utils_cman import PATH_CLUSTERCONF
from ..utils_corosync import PATH_COROCONF


@Command.deco(('ccspcmk2pcscmd',
                  ('stringiter-combine2')),
              ('cib2pcscmd',
                  ('stringiter-combine2')))
def pcs2pcscmd_flatiron(cmd_ctxt,
                        ccs=PATH_CLUSTERCONF,
                        cib=PATH_CIB,
                        output="-",
                        _common=XMLFilter.command_common):
    """(Corosync/CMAN,Pacemaker) cluster cfg. -> reinstating pcs commands

    Options:
        ccs       input Corosync/CMAN (+fencing pass-through) config. file
        cib       input proper Pacemaker cluster config. file
        output    pcs commands to reinstate the cluster per the inputs
    """

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        (
           file_proto(ccs),
           (
               file_proto(output),
           ),
           file_proto(cib),
           #(
           #    file_proto(output),  # already tracked
           #),
        ),
    )


@Command.deco(('simpleconfig2needlexml',
                  ('needlexml2pcscmd',
                      ('stringiter-combine2'))),
              ('cib2pcscmd',
                      ('stringiter-combine2')))
def pcs2pcscmd_needle(cmd_ctxt,
                      coro=PATH_COROCONF,
                      cib=PATH_CIB,
                      output="-",
                      _common=XMLFilter.command_common):
    """[COMMAND CURRENTLY UNAVAILABLE]

    Options:
        coro      input Corosync v2 config. file
        cib       input proper Pacemaker cluster config. file
        output    pcs commands to reinstate the cluster per the inputs
    """
    #"""(Corosync v2,Pacemaker) cluster cfg. -> reinstating pcs commands

    raise NotImplementedError("expected to come soon")

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        (
            file_proto(coro),
            (
                (
                    file_proto(coro),
                ),
            ),
           file_proto(cib),
           #(
           #    file_proto(output),  # already tracked
           #),
        ),
    )


@CommandAlias.deco
def pcs2pcscmd(cmds, *sys_id):
    # cluster_pcs_needle assumed unless "cluster_pcs_flatiron"
    return (pcs2pcscmd_flatiron if cluster_pcs_flatiron(*sys_id) else
            pcs2pcscmd_needle)
