# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing format"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
from lxml import etree
from os.path import dirname, join
#from pprint import pprint

import _bootstrap  # known W402, required

from clufter.format import FormatError
from clufter.formats.ccs import ccs
from clufter.formats.coro import coroxml_needle


class XMLFormatWalkTestCase(unittest.TestCase):
    walk_dir = join(dirname(__file__), 'XMLFormat-walk')
    result_walk_full = {
        'cluster': ('cluster-full', {
            'clusternodes': ('clusternodes-full', {
                'clusternode': ('clusternode-full', {
                })
            }),
            'cman': ('cman-full', {
            }),
            'dlm': ('dlm-full', {
            }),
            'rm': ('rm-full', {
                'failoverdomains': ('failoverdomains-full', {
                    'failoverdomain': ('failoverdomain-full', {
                    })
                }),
                'service': ('service-full', {
                })
            })
        })
    }
    result_walk_sparse = {
        'failoverdomain': ('failoverdomain-sparse', {
        }),
        'heuristic': ('heuristic-sparse', {
        })
    }

    def testWalkFull(self):
        r = ccs.walk_schema(self.walk_dir, 'full')
        #pprint(r, width=8)  # --> expected
        self.assertTrue(r == self.result_walk_full)

    def testWalkSparse(self):
        r = ccs.walk_schema(self.walk_dir, 'sparse')
        #pprint(r, width=8)  # --> expected
        self.assertTrue(r == self.result_walk_sparse)


class XMLValidationTestCase(unittest.TestCase):
    coro_input_ok = join(dirname(__file__), 'coro_ok.xml')
    coro_input_fail = join(dirname(__file__), 'coro_fail.xml')

    def testRngImplicitValidationOk(self):
        try:
            et = coroxml_needle('file', self.coro_input_ok)('etree')
        except Exception:
            raise
            self.assertTrue(False)

    def testRngImplicitValidationFail(self):
        try:
            et = coroxml_needle('file', self.coro_input_fail)('etree')
        except FormatError as e:
            self.assertTrue('Validation' in str(e))
            pass
        else:
            self.assertTrue(False)

    def testRngExplicitValidationOk(self):
        et, entries = coroxml_needle.etree_validator(
            etree.parse(self.coro_input_ok)
        )
        self.assertFalse(entries)

    def testRngExplicitValidationFail(self):
        et, entries = coroxml_needle.etree_validator(
            etree.parse(self.coro_input_fail)
        )
        self.assertTrue(entries)


if __name__ == '__main__':
    unittest.main()
