# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Format manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from .format import formats
from .plugin_registry import PluginManager


class FormatManager(PluginManager):
    """Class responsible for available formats of data to be converted"""
    _default_registry = formats

    def _init_handle_plugins(self, formats):
        self._formats = formats

    @property
    def formats(self):
        return self._formats.copy()
