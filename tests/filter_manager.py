# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
from os.path import dirname, join

import _bootstrap  # known W402, required

from clufter.format_manager import FormatManager
from clufter.filter_manager import FilterManager
from clufter.filters.ccs2ccsflat import ccs2ccsflat
from clufter.filters.ccsflat2pcs import ccsflat2pcs


class FilterManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.flt_mgr = FilterManager(FormatManager())

    def tearDown(self):
        self.flt_mgr.registry.setup(True)  # start from scratch
        self.flt_mgr = None


class Default(FilterManagerTestCase):
    def test_default(self):
        filters = self.flt_mgr.filters
        #print filters
        for cls in ccs2ccsflat, ccsflat2pcs:
            self.assertTrue(cls.name in filters)
            self.assertEqual(cls, type(filters[cls.name]))

    def test_run_ccs2ccsflat(self):
        # using ./empty.conf
        testfile = join(dirname(__file__), 'empty.conf')
        self.assertTrue('ccs2ccsflat' in self.flt_mgr.filters)
        out_obj = self.flt_mgr('ccs2ccsflat', ('file', testfile))
        # XXX print out_obj('bytestring')


if __name__ == '__main__':
    unittest.main()
