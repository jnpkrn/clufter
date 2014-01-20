# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Machinery entry point"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from .format_manager import FormatManager
from .filter_manager import FilterManager
from .command_manager import CommandManager
from .utils import EC
from . import version_line


def run(argv):
    ec = EC.EXIT_SUCCESS
    if len(argv) > 1 and argv[1] in ('-v', '--version'):
        print version_line()
    else:
        #try:
        cm = CommandManager(FilterManager(FormatManager()))
        ec = cm(argv)
        #except Exception as e:
        #    print "FATAL: Unhandled exception: {0}".format(e)
        #    ex = EC.EXIT_FAILURE
    return ec
