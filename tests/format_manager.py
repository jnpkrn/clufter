# -*- coding: UTF-8 -*-
# Copyright 2012 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing format manager"""
__author__ = "Jan Pokorný <jpokorny at redhat dot com>"

import unittest

import _bootstrap  # known W402, required

from clufter.format_manager import FormatManager
from clufter.formats.ccs import ccs
from clufter.formats.ccs import ccsflat
from clufter.formats.pcs import pcs


class FormatManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.fmt_mgr = FormatManager()

    def tearDown(self):
        self.fmt_mgr.registry.setup(True)  # start from scratch
        self.fmt_mgr = None


class Default(FormatManagerTestCase):
    def test_default(self):
        formats = self.fmt_mgr.formats
        #print formats
        for cls in ccs, ccsflat, pcs:
            self.assertTrue(cls.__name__ in formats)
            # the first was needed in the past, but now the more restrictive
            # one is ok
            self.assertEqual(type(cls), type(formats[cls.__name__]))
            self.assertEqual(cls, formats[cls.__name__])


class Injection(FormatManagerTestCase):
    formats = {'frobniccs': ccs}

    def setUp(self):
        self.fmt_mgr = FormatManager(paths=None, formats=self.formats)

    def test_injection(self):
        formats = self.fmt_mgr.formats
        #print formats
        self.assertTrue(len(formats) == len(self.formats))
        for fmt_id, fmt_cls in self.formats.iteritems():
            self.assertTrue(fmt_id in formats)
            self.assertEqual(fmt_cls, formats[fmt_id])


if __name__ == '__main__':
    unittest.main()
