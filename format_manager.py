# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Format manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from .format import formats


class FormatManager(object):
    """Class responsible for available formats of data to be converted"""
    def __init__(self, registry=formats, paths=(), formats={}):
        self._registry = registry
        self._formats = dict(registry.discover(paths), **formats)

    @property
    def registry(self):
        return self._registry

    @property
    def formats(self):
        return self._formats.copy()
