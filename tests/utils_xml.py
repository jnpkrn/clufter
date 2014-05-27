# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing XML helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest

import _bootstrap  # known W402, required

from lxml import etree
from os.path import dirname, join

from clufter.utils_xml import rng_pivot
from clufter.utils_prog import dirname_x


class TestRngPivot(unittest.TestCase):
    def test_rng_pivot(self):
        #p = join(dirname_x(__file__, 2), 'formats', 'corosync', 'corosync.rng')
        p = join(dirname(__file__), 'corosync.rng')
        with open(p) as f:
            et = etree.parse(f)
        ret = rng_pivot(et, 'logging')
        p = join(dirname(__file__), 'corosync.rng.exp')
        if False:  # to regenerate the expected file (manual review)
            with open(p, 'w') as f:
                f.write(etree.tostring(ret))
        else:
            with open(p) as f:
                expected = f.read()
            self.assertTrue(etree.tostring(ret) == expected)
