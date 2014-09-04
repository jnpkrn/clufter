# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing ccs2coro filter(s)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import dirname, join

from _common import CommonFilterTestCase


class Main(CommonFilterTestCase):
    def test01(self):
        # using ./filled.conf
        testfile = join(dirname(__file__), 'filled.conf')
        out_obj = self.flt_mgr('ccs2ccsflat', ('file', testfile))
        out_obj = self.flt_mgr('ccs2needlexml', ('etree', out_obj('etree')),
                               validator_specs={'':''})
        print out_obj('bytestring')
