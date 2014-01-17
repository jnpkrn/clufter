# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .command import commands
from .plugin_registry import PluginManager

log = logging.getLogger(__name__)


class CommandManager(PluginManager):
    """Class responsible for commands routing to filters or other actions"""
    _default_registry = commands

    def _handle_plugins(self, commands):
        self._commands = commands

    @property
    def commands(self):
        return self._commands.copy()

    def __call__(self, args):
        pass
        # self.filter_manager(string)
