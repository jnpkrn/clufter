# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
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
from ._chains_pcs import cib2pcscmd_chain_exec


@Command.deco(('cmd-annotate',
                          ('stringiter-combine3',
                              ('cmd-wrap'))),
              ('ccspcmk2pcscmd',
                          ('stringiter-combine3'  # , ('cmd-wrap' ...
                           )),
              (cib2pcscmd_chain_exec(
                          ('stringiter-combine3'  # , ('cmd-wrap' ...
                           ))))
def pcs2pcscmd_flatiron(cmd_ctxt,
                        ccs=PATH_CLUSTERCONF,
                        cib=PATH_CIB,
                        output="-",
                        force=False,
                        noauth=False,
                        silent=False,
                        tmp_cib="{cib2pcscmd.defs[pcscmd_tmpcib]}",
                        dry_run=False,
                        enable=False,
                        start_wait="{ccspcmk2pcscmd.defs[pcscmd_start_wait]}",
                        noguidance=False,
                        text_width='0',
                        _common=XMLFilter.command_common):
    """(Corosync/CMAN,Pacemaker) cluster cfg. -> reinstating pcs commands

    Options:
        ccs         input Corosync/CMAN (+fence_pcmk) configuration file
        cib         input proper Pacemaker cluster config. file (CIB)
        output      pcs commands to reinstate the cluster per the inputs
        force       may the force be with emitted pcs commands
        noauth      skip authentication step (OK if already set up)
        silent      do not track the progress along the steps execution (echoes)
        tmp_cib     file to accumulate the changes (empty ~ direct push, avoid!)
        dry_run     omit intrusive commands (TMP_CIB reset if empty)
        enable      enable cluster infrastructure services (autostart on reboot)
        start_wait  fixed seconds to give cluster to come up initially
        noguidance  omit extraneous guiding
        text_width  for commands rewrapping (0/-1/neg. ~ auto/disable/hi-limit)
    """
    cmd_ctxt['pcscmd_force'] = force
    cmd_ctxt['pcscmd_noauth'] = noauth
    cmd_ctxt['pcscmd_verbose'] = not(silent)
    cmd_ctxt['pcscmd_tmpcib'] = tmp_cib
    cmd_ctxt['pcscmd_dryrun'] = dry_run
    cmd_ctxt['pcscmd_enable'] = enable
    cmd_ctxt['pcscmd_start_wait'] = start_wait
    cmd_ctxt['pcscmd_noguidance'] = noguidance
    cmd_ctxt['text_width'] = text_width
    # XXX possibility to disable cib-meld-templates

    void_proto = protocols.plugins['void'].ensure_proto
    file_proto = protocols.plugins['file'].ensure_proto

    return (
        (
            void_proto(),
            (
                    (
                        file_proto(output),
                    ),
            ),
            file_proto(ccs),
            # already tracked
            #(
            #        (
            #            file_proto(output),
            #        ),
            #),
            file_proto(cib),
            # already tracked
            #cib2pcscmd_output(
            #        (
            #            file_proto(output),
            #        ),
            #),
        ),
    )


@Command.deco(('cmd-annotate',
                          ('stringiter-combine4',
                              ('cmd-wrap'))),
              ('simpleconfig-normalize',
                  ('simpleconfig2needlexml',
                      ('needlexml2pcscmd',
                          ('stringiter-combine4'  # , ('cmd-wrap' ...
                           )),
                      ('needleqdevicexml2pcscmd',
                          ('stringiter-combine4'  # , ('cmd-wrap' ...
                           )))),
              (cib2pcscmd_chain_exec(
                          ('stringiter-combine4'  # , ('cmd-wrap' ...
                           ))))
def pcs2pcscmd_needle(cmd_ctxt,
                      coro=PATH_COROCONF,
                      cib=PATH_CIB,
                      output="-",
                      force=False,
                      noauth=False,
                      silent=False,
                      tmp_cib="{cib2pcscmd.defs[pcscmd_tmpcib]}",
                      dry_run=False,
                      enable=False,
                      start_wait="{needlexml2pcscmd.defs[pcscmd_start_wait]}",
                      noguidance=False,
                      text_width='0',
                      _common=XMLFilter.command_common):
    """(Corosync v2,Pacemaker) cluster cfg. -> reinstating pcs commands

    Options:
        coro        input Corosync v2 configuration file
        cib         input proper Pacemaker cluster config. file (CIB)
        output      pcs commands to reinstate the cluster per the inputs
        force       may the force be with emitted pcs commands
        noauth      skip authentication step (OK if already set up)
        silent      do not track the progress along the steps execution (echoes)
        tmp_cib     file to accumulate the changes (empty ~ direct push, avoid!)
        dry_run     omit intrusive commands (TMP_CIB reset if empty)
        enable      enable cluster infrastructure services (autostart on reboot)
        start_wait  fixed seconds to give cluster to come up initially
        noguidance  omit extraneous guiding
        text_width  for commands rewrapping (0/-1/neg. ~ auto/disable/hi-limit)
    """
    cmd_ctxt['pcscmd_force'] = force
    cmd_ctxt['pcscmd_noauth'] = noauth
    cmd_ctxt['pcscmd_verbose'] = not(silent)
    cmd_ctxt['pcscmd_tmpcib'] = tmp_cib
    cmd_ctxt['pcscmd_dryrun'] = dry_run
    cmd_ctxt['pcscmd_enable'] = enable
    cmd_ctxt['pcscmd_start_wait'] = start_wait
    cmd_ctxt['pcscmd_noguidance'] = noguidance
    cmd_ctxt['text_width'] = text_width
    # XXX possibility to disable cib-meld-templates

    void_proto = protocols.plugins['void'].ensure_proto
    file_proto = protocols.plugins['file'].ensure_proto
    return (
        (
            void_proto(),
            (
                        (
                            file_proto(output),
                        ),
            ),
            file_proto(coro),
            # already tracked
            #(
            #    (
            #        (
            #            (
            #                file_proto(output),
            #            ),
            #        ),
            #        # already tracked
            #        #(
            #        #    (
            #        #        file_proto(output),
            #        #    ),
            #        #),
            #    ),
            #),
            file_proto(cib),
            # already tracked
            #cib2pcscmd_output(
            #            (
            #                file_proto(output),
            #            ),
            #),
        ),
    )


@CommandAlias.deco
def pcs2pcscmd(cmds, *sys_id):
    # cluster_pcs_needle assumed unless "cluster_pcs_flatiron"
    return (pcs2pcscmd_flatiron if cluster_pcs_flatiron(*sys_id) else
            pcs2pcscmd_needle)
