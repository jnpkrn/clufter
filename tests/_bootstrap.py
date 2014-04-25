# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Bootstrap the environment for testing"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from sys import path
from os.path import dirname, abspath


if __name__ != 'main_bootstrap':
    # if not run from main-bootstrap, verbose logging desired
    from os import environ
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(environ.get('LOGLEVEL', logging.DEBUG))

path.insert(0, reduce(lambda x, y: dirname(x), xrange(3), abspath(__file__)))
