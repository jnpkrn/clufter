# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2pcscmd{,-flatiron,-needle} commands"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command, CommandAlias
try:
    from ..defaults import SHELL_BASHLIKE, SHELL_POSIX
except ImportError:
    SHELL_BASHLIKE, SHELL_POSIX = ''
from ..facts import cluster_pcs_flatiron
from ..filter import XMLFilter
from ..protocol import protocols
from ..utils_cman import PATH_CLUSTERCONF
from ._chains_pcs import ccsflat2pcscmd_chain_exec, output_set_exec


@Command.deco(('cmd-annotate',
                                  ('stringiter-combine3',
                                      ('cmd-wrap'))),
              ('ccs2ccsflat',
                  ('ccs-disable-rg',
                      ('ccs2ccs-pcmk',
                          ('ccs-version-bump',
                              ('ccspcmk2pcscmd',
                                  ('stringiter-combine3'  # , ('cmd-wrap' ...
                                   ))))),
                  (ccsflat2pcscmd_chain_exec(
                                  ('stringiter-combine3'  # , ('cmd-wrap' ...
                                   )))))
def ccs2pcscmd_flatiron(cmd_ctxt,
                        input=PATH_CLUSTERCONF,
                        output="-",
                        force=False,
                        noauth=False,
                        silent=False,
                        tmp_cib="{cib2pcscmd.defs[pcscmd_tmpcib]}",
                        dry_run=False,
                        enable=False,
                        start_wait="{ccspcmk2pcscmd.defs[pcscmd_start_wait]}",
                        noguidance=False,
                        set_exec=False,
                        text_width='0',
                        _common=XMLFilter.command_common):
    """(CMAN,rgmanager) cluster cfg. -> equivalent in pcs commands

    Options:
        input       input (CMAN,rgmanager) cluster configuration file
        output      pcs commands to reinstate the cluster per the inputs
        force       may the force be with emitted pcs commands
        noauth      skip authentication step (OK if already set up)
        silent      do not track the progress along the steps execution (echoes)
        tmp_cib     file to accumulate the changes (empty ~ direct push, avoid!)
        dry_run     omit intrusive commands (TMP_CIB reset if empty)
        enable      enable cluster infrastructure services (autostart on reboot)
        start_wait  fixed seconds to give cluster to come up initially
        noguidance  omit extraneous guiding
        set_exec    make the output file executable (not recommended)
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

    # possible use of process substitution (https://bugzilla.redhat.com/1381531)
    cmd_ctxt['annotate_shell'] = (SHELL_POSIX if dry_run or noguidance
                                  else SHELL_BASHLIKE)
    # XXX possibility to disable cib-meld-templates

    void_proto = protocols.plugins['void'].ensure_proto
    file_proto = protocols.plugins['file'].ensure_proto
    yield (
        (
            void_proto(),
            (
                                                (
                                                    file_proto(output),
                                                ),
            ),
        ), (
            file_proto(input),
            # already tracked
            #(
            #    (
            #        (
            #            (
            #                (
            #                                    (
            #                                        file_proto(output),
            #                                    ),
            #                ),
            #            ),
            #        ),
            #    ),
            #    # already tracked
            #    #ccsflat2pcscmd_output(
            #    #                                (
            #    #                                    file_proto(output),
            #    #                                ),
            #    #),
            #),
        ),
    )
    # post-processing (make resulting file optionally executable)
    if set_exec:
        output_set_exec(cmd_ctxt, 'cmd-wrap')


@Command.deco(('cmd-annotate',
                              ('stringiter-combine4',
                                  ('cmd-wrap'))),
              ('ccs2ccsflat',
                  ('ccs-propagate-cman',
                      ('ccs2needlexml',
                          ('needlexml2pcscmd',
                              ('stringiter-combine4'  # , ('cmd-wrap' ...
                               )),
                          ('needleqdevicexml2pcscmd',
                              ('stringiter-combine4'  # , ('cmd-wrap' ...
                               )))),
                  (ccsflat2pcscmd_chain_exec(
                              ('stringiter-combine4'  # , ('cmd-wrap' ...
                               )))))
def ccs2pcscmd_needle(cmd_ctxt,
                      input=PATH_CLUSTERCONF,
                      output="-",
                      force=False,
                      noauth=False,
                      silent=False,
                      tmp_cib="{cib2pcscmd.defs[pcscmd_tmpcib]}",
                      dry_run=False,
                      enable=False,
                      start_wait="{needlexml2pcscmd.defs[pcscmd_start_wait]}",
                      noguidance=False,
                      set_exec=False,
                      text_width='0',
                      _common=XMLFilter.command_common):
    """(CMAN,rgmanager) cluster cfg. -> equivalent in pcs commands

    Options:
        input       input (CMAN,rgmanager) cluster configuration file
        output      pcs commands to reinstate the cluster per the inputs
        force       may the force be with emitted pcs commands
        noauth      skip authentication step (OK if already set up)
        silent      do not track the progress along the steps execution (echoes)
        tmp_cib     file to accumulate the changes (empty ~ direct push, avoid!)
        dry_run     omit intrusive commands (TMP_CIB reset if empty)
        enable      enable cluster infrastructure services (autostart on reboot)
        start_wait  fixed seconds to give cluster to come up initially
        noguidance  omit extraneous guiding
        set_exec    make the output file executable (not recommended)
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

    # possible use of process substitution (https://bugzilla.redhat.com/1381531)
    cmd_ctxt['annotate_shell'] = (SHELL_POSIX if dry_run or noguidance
                                  else SHELL_BASHLIKE)
    # XXX possibility to disable cib-meld-templates

    void_proto = protocols.plugins['void'].ensure_proto
    file_proto = protocols.plugins['file'].ensure_proto
    yield (
        (
            void_proto(),
            (
                                                (
                                                    file_proto(output),
                                                ),
            ),
        ), (
            file_proto(input),
            #(
            #    (
            #        (
            #                                (
            #                                    (
            #                                        file_proto(output),
            #                                    ),
            #                                ),
            #            # already tracked
            #            #                    (
            #            #                        (
            #            #                            file_proto(output),
            #            #                        ),
            #            #                    ),
            #        ),
            #    ),
            #    # already tracked
            #    #ccsflat2pcscmd_output(
            #    #                                (
            #    #                                    file_proto(output),
            #    #                                ),
            #    #),
            #),
        ),
    )
    # post-processing (make resulting file optionally executable)
    if set_exec:
        output_set_exec(cmd_ctxt, 'cmd-wrap')


@CommandAlias.deco
def ccs2pcscmd(cmds, *sys_id):
    # cluster_pcs_needle assumed unless "cluster_pcs_flatiron"
    return (ccs2pcscmd_flatiron if cluster_pcs_flatiron(*sys_id) else
            ccs2pcscmd_needle)
