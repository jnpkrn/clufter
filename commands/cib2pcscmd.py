# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cib2pcscmd command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..filter import XMLFilter
from ..protocol import protocols
from ..utils_cib import PATH_CIB


@Command.deco(('cib-revitalize',
                  ('cib-meld-templates',
                      ('cib2pcscmd',
                          ('cmd-wrap')))))
def cib2pcscmd(cmd_ctxt,
               input=PATH_CIB,
               output="-",
               force=False,
               noauth=False,
               silent=False,
               tmp_cib="{cib2pcscmd.defs[pcscmd_tmpcib]}",
               dry_run=False,
               enable=False,
               text_width='0',
               _common=XMLFilter.command_common):
    """CIB -> equivalent in pcs commands

    Options:
        input       input (CMAN,rgmanager) cluster config. file
        output      pcs commands to reinstate the cluster per the inputs
        force       may the force be with emitted pcs commands
        noauth      skip authentication step (OK if already set up)
        silent      do not track the progress along the steps execution (echoes)
        tmp_cib     file to accumulate the changes (empty ~ direct push)
        dry_run     omit intrusive commands (TMP_CIB reset if empty)
        enable      enable cluster infrastructure services (autostart on reboot)
        text_width  for commands rewrapping (0/-1/neg. ~ auto/disable/hi-limit)
    """
    cmd_ctxt['pcscmd_force'] = force
    cmd_ctxt['pcscmd_noauth'] = noauth
    cmd_ctxt['pcscmd_verbose'] = not(silent)
    cmd_ctxt['pcscmd_tmpcib'] = tmp_cib
    cmd_ctxt['pcscmd_dryrun'] = dry_run
    cmd_ctxt['pcscmd_enable'] = enable
    cmd_ctxt['text_width'] = text_width
    # XXX possibility to disable cib-meld-templates

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
