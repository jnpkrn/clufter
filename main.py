# -*- coding: UTF-8 -*-
# Copyright 2012 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Machinery entry point"""
__author__ = "Jan Pokorný <jpokorny at redhat dot com>"

import sys
from .format_manager import FormatManager
from .filter_manager import FilterManager
from .command_manager import CommandManager
from .utils import EC
from . import metadata


def main(argv):
    ec = EC.SUCCESS
    if len(argv) and argv[0] in ('-v', '--version'):
        print '\n'.join(metadata)
    else:
        cm = CommandManager(FilterManager(FormatManager()))
        ec = cm(argv)
    return ec

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
