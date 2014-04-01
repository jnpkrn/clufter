# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2pcs command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command, CommandAlias


@Command.deco(('ccs2ccsflat',
                  ('ccs2ccs-pcmk'),
                  ('ccsflat2pcs'),
                  ('ccs2flatironxml',
                      ('xml2simpleconfig'))))
def ccs2pcs_flatiron(cmd_ctxt,
                     input="/etc/cluster/cluster.conf",
                     ccs_pcmk="./cluster.conf",
                     cib="./cib.xml",
                     coro="./corosync.conf",
                     nocheck=False):
    """CMAN -> Pacemaker-based cluster config. (corosync v1)

    More specifically, the output is suitable for Pacemaker integrated
    with Corosync ver. 1 (Flatiron) as present, e.g., in el6.{5, ..},
    and consists of Pacemaker pass-through CMAN configuration (~cluster.conf)
    along with Pacemaker (~cib.xml) and corosync ones (~corosync.conf).

    Options:
        input     input CMAN-based cluster configuration file
        ccs_pcmk  output Pacemaker pass-through CMAN configuration
        cib       output Pacemaker-based cluster configuration file
        coro      output Corosync v1 configuration file
        nocheck   do not validate any step (even if self-checks present)
    """
    #cmd_ctxt.filter()['validate'] = not nocheck
    #cmd_ctxt.filter('ccs2ccsflat')['validate'] = not nocheck
    return (
        ('file', input),
        (
            ('file', ccs_pcmk),
            ('file', cib),
            (
                ('file', coro),
            )
        )
    )


@Command.deco(('ccs2ccsflat',
                  ('ccsflat2pcs'),
                  ('ccs2needlexml',
                      ('xml2simpleconfig'))))
def ccs2pcs_needle(cmd_ctxt,
                   input="/etc/cluster/cluster.conf",
                   cib="./cib.xml",
                   coro="./corosync.conf",
                   nocheck=False):
    """CMAN -> Pacemaker-based cluster config. (corosync v2)

    More specifically, the output is suitable for Pacemaker integrated
    with Corosync ver. 2 (Needle) as present, e.g., in el7, and consists
    of Pacemaker (~cib.xml) and corosync (~corosync.conf) configurations.

    Options:
        input    input CMAN-based cluster configuration file
        cib      output Pacemaker-based cluster configuration file
        coro     output Corosync v2 configuration file
        nocheck  do not validate any step (even if self-checks present)
    """
    #cmd_ctxt.filter()['validate'] = not nocheck
    #cmd_ctxt.filter('ccs2ccsflat')['validate'] = not nocheck
    return (
        ('file', input),
        (
            ('file', cib),
            (
                ('file', coro),
            )
        )
    )


@CommandAlias.deco
def ccs2pcs(cmds, system, system_extra):
    # unless el <7.0 (XXX identification of SL and other derivates unknown)
    if system == 'Linux' and system_extra[0] in ('redhat', 'centos'):
        v = system_extra[1] if system_extra else '7'  # default if undecidable
        v = v[:-len(v.lstrip('0123456789.'))] or str.isdigit(v[0]) and v or '0'
        v = tuple(map(int, (v.rstrip('.') + '.0.0').split('.')[:2]))
        if v < (7, 0):
            return 'ccs2pcs-flatiron'
    return 'ccs2pcs-needle'
