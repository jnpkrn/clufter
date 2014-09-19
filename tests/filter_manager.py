# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os.path as op; execfile(op.join(op.dirname(__file__), '_bootstrap.py'))


from unittest import TestCase
from os.path import dirname, join

from lxml.doctestcompare import norm_whitespace

from .format_manager import FormatManager
from .format import formats
formats = formats.plugins
from .filter import Filter
from .filter_manager import FilterManager
from .utils import head_tail


class FilterManagerTestCase(TestCase):
    def setUp(self):
        self.flt_mgr = FilterManager(FormatManager())

    def tearDown(self):
        self.flt_mgr.registry.setup(True)  # start from scratch
        self.flt_mgr = None


class Default(FilterManagerTestCase):
    def test_default(self):
        # NOTE imports has to be just there due to environment changed
        #      by "starting from scratch" + plugin discovery elsewhere
        from .filters.ccs2ccsflat import ccs2ccsflat
        from .filters.ccsflat2pcs import ccsflat2pcs
        filters = self.flt_mgr.filters
        #print filters
        for cls in ccs2ccsflat, ccsflat2pcs:
            # CHECK selected built-in plugin is auto-discovered
            self.assertTrue(cls.name in filters)
            # CHECK it's class matches the class of natively imported one
            #       during this test-run (not generally due to "restart")
            self.assertTrue(cls is type(filters[cls.name]))

    def test_run_ccs2ccsflat(self):
        testfile = join(dirname(__file__), 'empty.conf')
        # CHECK the auto-discovered filter properly tracked
        self.assertTrue('ccs2ccsflat' in self.flt_mgr.filters)
        out_obj = self.flt_mgr('ccs2ccsflat', ('file', testfile))
        result = out_obj('bytestring')
        # XXX print result
        # CHECK the externalized representation matches the original
        with file(testfile) as f:
            self.assertEqual(norm_whitespace(result), norm_whitespace(f.read()))


class CompositeFormatIO(FilterManagerTestCase):
    """Exercising filters with composite formats"""
    def setUp(self):
        @Filter.deco(('ccs', 'ccs'), ('ccs-flat', 'ccs-flat'))
        def double_ccs2ccsflat(flt_ctxt, in_objs, verify=False):
            from .filters.ccs2ccsflat import ccs2ccsflat
            ccs2ccsflat = ccs2ccsflat(formats)
            outs = []
            for in_obj in in_objs:
                outs.append(('bytestring', ccs2ccsflat(in_obj)('bytestring')))
            subprotos, subresults = head_tail(zip(*outs))
            return ('composite', subprotos), subresults
        super(CompositeFormatIO, self).setUp()

    def test_run_double_ccs2ccsflat(self):
        testfile = join(dirname(__file__), 'empty.conf')
        # CHECK the filter defined in setUp method properly tracked
        self.assertTrue('double-ccs2ccsflat' in self.flt_mgr.filters)
        # perform the filter
        out_objs = self.flt_mgr('double-ccs2ccsflat',
            (('composite', ('file', 'file')), testfile, testfile)
        )
        # CHECK resulting objects are not identical (separate processing)
        # NOTE there could be heuristic to capture duplicated work, but such
        #      filter is phony anyway
        self.assertTrue(out_objs[0] is not out_objs[1])
        # externalize outputs
        results = out_objs(('composite', ('bytestring', 'bytestring')))
        # XXX print results
        # CHECK resulting externalized representation is, however, tha same
        self.assertEqual(*tuple(norm_whitespace for r in results))
        # CHECK picked externalized representation matches the original
        with file(testfile) as f:
            self.assertEqual(norm_whitespace(results[0]),
                             norm_whitespace(f.read()))


execfile(op.join(op.dirname(__file__), '_bootstart.py'))
