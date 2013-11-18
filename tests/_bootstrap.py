# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Bootstrap the environment for testing"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
logging.basicConfig(level=logging.DEBUG)

from sys import path
from os.path import dirname, abspath
path.insert(0, reduce(lambda x, y: dirname(x), xrange(3), abspath(__file__)))
