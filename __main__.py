# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Machinery entry point -- to be run via python{,2} -m <package>"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import basename
from sys import argv, executable, exit

from .main import run

if basename(argv[0]) == '__main__.py':
    # for help screens only, hence spaces allowed
    argv[0] = "{0} -m {1}".format(executable, __package__)
exit(run(argv))
