# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2pcs{,-flatiron,-needle} commands"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command, CommandAlias
from ..filter import XMLFilter
from ..protocol import protocols
from ..utils_cluster import cluster_pcs_1_2, cluster_pcs_flatiron


def _check_pacemaker_1_2(cmd_ctxt):
    system = cmd_ctxt.get('system', 'UNKNOWN-SYSTEM')
    system_extra = cmd_ctxt.get('system_extra', 'UNKNOWN-DISTRO')
    if not cluster_pcs_1_2(system, system_extra):
        from sys import stderr
        print >>stderr, ("Resulting configuration will likely not be applicable"
                         " to ``{0}'' system as it seems so outdated as far as"
                         " Pacemaker not supporting validation schema v1.2"
                        ).format(': '.join((system, system_extra)))


@Command.deco(('ccs2ccsflat',
                  ('ccs2ccs-pcmk'),
                  ('ccs-revitalize',
                      ('ccsflat2pcsprelude',
                          ('pcsprelude2pcscompact',
                              ('pcscompact2pcs',
                                  ('pcs2pcsfinal')))))))
def ccs2pcs_flatiron(cmd_ctxt,
                     input="/etc/cluster/cluster.conf",
                     ccs_pcmk="cluster-{ccs2ccsflat.in.hash}.conf",
                     cib="cib-{ccs2ccsflat.in.hash}.xml",
                     _common=XMLFilter.command_common):
    """CMAN -> Pacemaker-based cluster config. (corosync v1)

    More specifically, the output is suitable for Pacemaker integrated
    with Corosync ver. 1 (Flatiron) as present, e.g., in el6.{5, ..},
    and consists of Pacemaker pass-through CMAN configuration (~cluster.conf)
    along with Pacemaker (~cib.xml) one.

    Options:
        input     input CMAN-based cluster configuration file
        ccs_pcmk  output Pacemaker pass-through CMAN configuration
        cib       output Pacemaker-based cluster configuration file
    """
    _check_pacemaker_1_2(cmd_ctxt)

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        (
            file_proto(ccs_pcmk),
            (
                (
                    (
                        (
                            file_proto(cib),
                        ),
                    ),
                ),
            ),
        ),
    )


@Command.deco(('ccs2ccsflat',
                  ('ccs-revitalize',
                      ('ccsflat2pcsprelude',
                          ('pcsprelude2pcscompact',
                              ('pcscompact2pcs',
                                  ('pcs2pcsfinal'))))),
                  ('ccs2needlexml',
                      ('xml2simpleconfig'))))
def ccs2pcs_needle(cmd_ctxt,
                   input="/etc/cluster/cluster.conf",
                   cib="cib-{ccs2ccsflat.in.hash}.xml",
                   coro="corosync-{ccs2ccsflat.in.hash}.conf",
                   _common=XMLFilter.command_common):
    """CMAN -> Pacemaker-based cluster config. (corosync v2)

    More specifically, the output is suitable for Pacemaker integrated
    with Corosync ver. 2 (Needle) as present, e.g., in el7, and consists
    of Pacemaker (~cib.xml) and corosync (~corosync.conf) configurations.

    Options:
        input    input CMAN-based cluster configuration file
        cib      output Pacemaker-based cluster configuration file
        coro     output Corosync v2 configuration file
    """
    _check_pacemaker_1_2(cmd_ctxt)

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        (
            (
                (
                    (
                        (
                            file_proto(cib),
                        ),
                    ),
                ),
            ),
            (
                file_proto(coro),
            ),
        ),
    )


@CommandAlias.deco
def ccs2pcs(cmds, *sys_id):
    # cluster_pcs_needle assumed unless "cluster_pcs_flatiron"
    return ccs2pcs_flatiron if cluster_pcs_flatiron(*sys_id) else ccs2pcs_needle
