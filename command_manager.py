# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .command import commands
from .plugin_registry import PluginManager
from .utils import apply_preserving_depth, \
                   apply_aggregation_preserving_depth, \
                   apply_intercalate

log = logging.getLogger(__name__)


class CommandManager(PluginManager):
    """Class responsible for commands routing to filters or other actions"""
    _default_registry = commands

    def _handle_plugins(self, commands, flt_mgr):
        log.debug("Commands before resolving: {0}"
                  .format(commands))
        self._commands = self._resolve(flt_mgr.filters, commands)

    @staticmethod
    def _resolve(filters, commands):
        for cmd_name, cmd_cls in commands.items():
            res_input = cmd_cls.filter_chain
            res_output = apply_preserving_depth(filters.get)(res_input)
            if apply_aggregation_preserving_depth(all)(res_output):
                log.debug("resolve at `{0}' command: `{1}' -> {2}"
                          .format(cmd_name, repr(res_input), repr(res_output)))
                commands[cmd_name] = cmd_cls(*res_output)
                continue
            # drop the command if cannot resolve any of the filters
            res_input = apply_intercalate(res_input)
            log.debug("cmd_name {0}".format(res_input))
            map(lambda (i, x): log.warning("Resolve at `{0}' command:"
                                           " `{1}' (#{2}) filter fail"
                                           .format(cmd_name, res_input[i], i)),
                filter(lambda (i, x): not(x),
                       enumerate(apply_intercalate(res_output))))
            commands.pop(cmd_name)
        return commands

    @property
    def commands(self):
        return self._commands.copy()

    def __call__(self, args):
        # 1. figure out commands + inject artificial ones (help)
        #print self.commands
        raise NotImplementedError
        # commands =
        # 2. check if command matches define ones (or none = default?)
        # 2a. success -> pass further (TODO)
        # 2b. failure -> print help/diagnostics
