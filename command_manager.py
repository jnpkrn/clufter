# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


class CommandManager(object):
    """Class responsible for commands routing to filters or other actions"""
    def __init__(self, filter_manager):
        self.filter_manager = filter_manager

    def __call__(self, args):
        pass
        # self.filter_manager(string)
