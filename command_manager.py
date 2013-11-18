# -*- coding: UTF-8 -*-
# Copyright 2012 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)


class CommandManager(object):
    """Class responsible to route commands to filters or other actions"""
    def __init__(self, filter_manager):
        self.filter_manager = filter_manager

    def __call__(self, args):
        pass
        # self.filter_manager(string)
