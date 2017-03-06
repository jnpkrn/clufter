# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing format"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from os.path import dirname, join
from unittest import TestCase
#from pprint import pprint

from lxml import etree

from .format import FormatError
from .formats.ccs import ccs
from .formats.coroxml import coroxml_needle
from .utils import head_tail


class XMLFormatWalkTestCase(TestCase):
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
        self.assertEqual(r, self.result_walk_full)

    def testWalkSparse(self):
        r = ccs.walk_schema(self.walk_dir, 'sparse')
        #pprint(r, width=8)  # --> expected
        self.assertEqual(r, self.result_walk_sparse)


class XMLValidationTestCase(TestCase):
    coro_input_ok = join(dirname(__file__), 'coro_ok.xml')
    coro_input_fail = join(dirname(__file__), 'coro_fail.xml')

    def testRngImplicitValidationOk(self):
        ok = True
        try:
            et = coroxml_needle('file', self.coro_input_ok)('etree')
        except Exception:
            ok = False
        self.assertTrue(ok)

    def testRngImplicitValidationFail(self):
        try:
            et = coroxml_needle('file', self.coro_input_fail)('etree')
        except FormatError as e:
            self.assertTrue('Validation' in str(e))
            pass
        else:
            self.assertTrue(False)

    def testRngExplicitValidationOk(self):
        entries, _ = head_tail(coroxml_needle.etree_validator(
            etree.parse(self.coro_input_ok)
        ))
        self.assertFalse(entries)

    def testRngExplicitValidationFail(self):
        entries, _ = head_tail(coroxml_needle.etree_validator(
            etree.parse(self.coro_input_fail)
        ))
        self.assertTrue(entries)


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
