# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest

import _bootstrap  # known W402, required

from clufter.format_manager import FormatManager
from clufter.filter_manager import FilterManager


class CommonFilterTestCase(unittest.TestCase):
    def setUp(self):
        self.flt_mgr = FilterManager(FormatManager())

    #def tearDown(self):
    #    self.flt_mgr.registry.setup(True)  # start from scratch
    #    self.flt_mgr = None
