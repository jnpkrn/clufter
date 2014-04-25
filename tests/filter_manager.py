# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
from os.path import dirname, join

import _bootstrap  # known W402, required

from clufter.format_manager import FormatManager
from clufter.filter import Filter
from clufter.filter_manager import FilterManager
from clufter.utils import head_tail


class FilterManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.flt_mgr = FilterManager(FormatManager())

    def tearDown(self):
        self.flt_mgr.registry.setup(True)  # start from scratch
        self.flt_mgr = None


class Default(FilterManagerTestCase):
    def test_default(self):
        # NOTE imports has to be just there due to environment changed
        #      by "starting from scratch" + plugin discovery elsewhere
        from clufter.filters.ccs2flatccs import ccs2flatccs
        from clufter.filters.flatccs2pcs import flatccs2pcs
        filters = self.flt_mgr.filters
        #print filters
        for cls in ccs2flatccs, flatccs2pcs:
            # CHECK selected built-in plugin is auto-discovered
            self.assertTrue(cls.name in filters)
            # CHECK it's class matches the class of natively imported one
            #       during this test-run (not generally due to "restart")
            self.assertTrue(cls is type(filters[cls.name]))

    def test_run_ccs2flatccs(self):
        testfile = join(dirname(__file__), 'empty.conf')
        # CHECK the auto-discovered filter properly tracked
        self.assertTrue('ccs2flatccs' in self.flt_mgr.filters)
        out_obj = self.flt_mgr('ccs2flatccs', ('file', testfile))
        result = out_obj('bytestring')
        # XXX print result
        # CHECK the externalized representation matches the original
        with file(testfile) as f:
            self.assertEqual(result, f.read())


class CompositeFormatIO(FilterManagerTestCase):
    """Exercising filters with composite formats"""
    def setUp(self):
        @Filter.deco(('ccs', 'ccs'), ('flatccs', 'flatccs'))
        def double_ccs2flatccs(flt_ctxt, in_objs, verify=False):
            from clufter.filters.ccs2flatccs import ccs2flatccs
            from clufter.formats.ccs import ccs, flatccs
            ccs2flatccs = ccs2flatccs(ccs, flatccs)
            outs = []
            for in_obj in in_objs:
                outs.append(('bytestring', ccs2flatccs(in_obj)('bytestring')))
            subprotos, subresults = head_tail(zip(*outs))
            return ('composite', subprotos), subresults
        super(CompositeFormatIO, self).setUp()

    def test_run_double_ccs2flatccs(self):
        testfile = join(dirname(__file__), 'empty.conf')
        # CHECK the filter defined in setUp method properly tracked
        self.assertTrue('double-ccs2flatccs' in self.flt_mgr.filters)
        # perform the filter
        out_objs = self.flt_mgr('double-ccs2flatccs',
            (('composite', ('file', 'file')), testfile, testfile)
        )
        # CHECK resulting objects are not identical (separate processing)
        # NOTE there could be heuristic to capture duplicated work, but such
        #      filter is phony anyway
        self.assertTrue(out_objs[0] is not out_objs[1])
        # externalize outputs
        results = out_objs(('composite', ('bytestring', 'bytestring')))
        # XXX print results
        # CHECK resulting externalized reprezentation is, however, tha same
        self.assertEqual(*results)
        # CHECK picked externalized representation matches the original
        with file(testfile) as f:
            self.assertEqual(results[0], f.read())


if __name__ == '__main__':
    unittest.main()
