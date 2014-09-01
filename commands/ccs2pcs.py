# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2pcs command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command, CommandAlias
from ..filter import XMLFilter
from ..protocol import protocols


@Command.deco(('ccs2flatccs',
                  ('ccs2ccs-pcmk'),
                  ('ccs-revitalize',
                      ('flatccs2pcs',
                          ('pcs2simplepcs')))))
def ccs2pcs_flatiron(cmd_ctxt,
                     input="/etc/cluster/cluster.conf",
                     ccs_pcmk="cluster.conf",
                     cib="cib.xml",
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
    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        (
            file_proto(ccs_pcmk),
            (
                (
                    file_proto(cib),
                ),
            ),
        ),
    )


@Command.deco(('ccs2flatccs',
                  ('ccs-revitalize',
                      ('flatccs2pcs',
                          ('pcs2simplepcs'))),
                  ('ccs2needlexml',
                      ('xml2simpleconfig'))))
def ccs2pcs_needle(cmd_ctxt,
                   input="/etc/cluster/cluster.conf",
                   cib="cib.xml",
                   coro="corosync.conf",
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
    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        (
            (
                (
                    file_proto(cib),
                ),
            ),
            (
                file_proto(coro),
            ),
        ),
    )


@CommandAlias.deco
def ccs2pcs(cmds, system, system_extra):
    # unless el <7.0 (XXX identification of SL and other derivates unknown)
    if system == 'linux' and system_extra[0] in ('redhat', 'centos'):
        v = system_extra[1] if system_extra else '7'  # default if undecidable
        v = v[:-len(v.lstrip('0123456789.'))] or str.isdigit(v[0]) and v or '0'
        v = tuple(map(int, (v.rstrip('.') + '.0.0').split('.')[:2]))
        if v < (7, 0):
            return 'ccs2pcs-flatiron'
    return 'ccs2pcs-needle'
