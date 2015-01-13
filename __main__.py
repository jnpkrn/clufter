# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Machinery entry point -- to be run via python -m <package>"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import basename
from sys import argv, exit

from .main import run

if basename(argv[0]) == '__main__.py':
    argv[0] = 'python -m ' + __package__
exit(run(argv))
