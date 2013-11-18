# -*- coding: UTF-8 -*-
# Copyright 2012 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ..command import as_command


@as_command(['ccs2ccsflat', ('ccs2pcs', 'ccs2coro')])
def ccs2pcs(input='/etc/cluster/cluster.conf',
            output='./cib.xml',
            coro='/.corosync.conf'):
    """Converts cman-based cluster configuration to Pacemaker-based one

    Options:
        input      input cman-based cluster configuration file
        output     output pacemaker-based configuration file
        coro       output Corosync configuration file
    """
    return ('file', input), (('file', output), ('file', coro))
