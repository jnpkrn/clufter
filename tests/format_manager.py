# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing format manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os.path as op; execfile(op.join(op.dirname(__file__), '_bootstrap.py'))


from unittest import TestCase

from .format_manager import FormatManager
from .formats.ccs import ccs
from .formats.ccs import ccs_flat
from .formats.pcs import pcs


class FormatManagerTestCase(TestCase):
    def setUp(self):
        self.fmt_mgr = FormatManager()

    def tearDown(self):
        self.fmt_mgr.registry.setup(True)  # start from scratch
        self.fmt_mgr = None


class Default(FormatManagerTestCase):
    def test_default(self):
        formats = self.fmt_mgr.formats
        #print formats
        for cls in ccs, ccs_flat, pcs:
            self.assertTrue(cls.__name__ in formats)
            # the first was needed in the past, but now the more restrictive
            # one is ok
            self.assertEqual(type(cls), type(formats[cls.__name__]))
            self.assertEqual(cls, formats[cls.__name__])


class Injection(FormatManagerTestCase):

    def setUp(self):
        self.formats = {'frobniccs': ccs}
        self.fmt_mgr = FormatManager(paths=None, plugins=self.formats)

    def test_injection(self):
        formats = self.fmt_mgr.formats
        #print formats
        self.assertTrue(len(formats) == len(self.formats))
        for fmt_id, fmt_cls in self.formats.iteritems():
            self.assertTrue(fmt_id in formats)
            self.assertEqual(fmt_cls, formats[fmt_id])


execfile(op.join(op.dirname(__file__), '_bootstart.py'))
