# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Common base for testing"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from unittest import TestCase

from .filter_manager import FilterManager


class CommonFilterTestCase(TestCase):
    def setUp(self):
        self.flt_mgr = FilterManager.init_lookup(ext_plugins=False)

    #def tearDown(self):
    #    self.flt_mgr.registry.setup(True)  # start from scratch
    #    self.flt_mgr = None
