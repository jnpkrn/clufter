# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""pcs_resource_deps command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..filter import XMLFilter
from ..protocol import protocols

@Command.deco(('pcs-resource-deps',
                   ('stringlist2stringset',
                        ('pkgs2distropkgs',
                            ('pkgs2installcmd')))))
def pcs_rsc_deps(cmd_ctxt,
                 input="/var/lib/pacemaker/cib/cib.xml",
                 output="pcs-resource-deps-{pcs-resource-deps.in.hash}.conf",
                 install_cmd=False,
                 _common=XMLFilter.command_common):
    """Output deps of resources contained in Pacemaker cfg.

    Options:
        input        input Pacemaker configuration file
        output       output file with collected dependencies
        install_cmd  whether to output full install command instead
    """
    #if not install_cmd:
    #    cmd_ctxt['filter_noop'].append('pkgs2installcmd')

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        (
            (
                (
                    file_proto(output),
                ),
            ),
        ),
    )
