# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
from os.path import dirname, join
#from pprint import pprint

import _bootstrap  # known W402, required

from clufter.formats.ccs import ccs

WALK_DIR = join(dirname(__file__), 'XMLFormat-walk')

RESULT_WALK_FULL = {
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

RESULT_WALK_SPARSE = {
    'failoverdomain': ('failoverdomain-sparse', {
    }),
    'heuristic': ('heuristic-sparse', {
    })
}


class XMLFormatWalkTestCase(unittest.TestCase):
    def testWalkFull(self):
        r = ccs.walk_schema(WALK_DIR, 'full')
        #pprint(r, width=8)  # --> expected
        self.assertTrue(r == RESULT_WALK_FULL)

    def testWalkSparse(self):
        r = ccs.walk_schema(WALK_DIR, 'sparse')
        #pprint(r, width=8)  # --> expected
        self.assertTrue(r == RESULT_WALK_SPARSE)


if __name__ == '__main__':
    unittest.main()
