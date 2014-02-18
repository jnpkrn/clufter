# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2pcs command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command


@Command.deco(('ccs2ccsflat',
               'ccsflat2pcs', ('ccs2coroxml', 'xml2simpleconfig')))
def ccs2pcs(cmd_ctxt,
            input='/etc/cluster/cluster.conf',
            output='./cib.xml',
            coro='./corosync.conf',
            nocheck=False):
    """Converts cman-based cluster configuration to Pacemaker-based one

    There are two outputs: Pacemaker configuration ala cib.xml and
    configuration for corosync ala corosync.conf.

    Options:
        input      input cman-based cluster configuration file
        output     output pacemaker-based configuration file
        coro       output Corosync configuration file
        nocheck    do not validate any step (even if self-checks present)
    """
    #cmd_ctxt.filter()['validate'] = not nocheck
    #cmd_ctxt.filter('ccs2ccsflat')['validate'] = not nocheck
    return ('file', input), (('file', output), (('file', coro), ))
