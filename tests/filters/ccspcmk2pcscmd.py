# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing `ccspcmk2pcscmd' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
flt = 'ccspcmk2pcscmd'
ccspcmk2pcscmd = FilterManager.init_lookup(flt).filters[flt]
ccs = ccspcmk2pcscmd.in_format


class FiltersCcspcmk2pcscmdTestCase(TestCase):
    def testConversion(self):
        in_obj = ccs('file', join(dirname(dirname(__file__)), 'filled.conf'))
        ret = ccspcmk2pcscmd(in_obj, pcscmd_verbose=False, pcscmd_noauth=True,
                                     pcscmd_noguidance=True)
        #print ret.BYTESTRING()
        self.assertEquals(
            ret.BYTESTRING(),
            "pcs cluster setup --name test ju hele"
            " --consensus 200 --join 100 --token 5000\n"
            "pcs cluster start --all --wait=-1 && sleep {sleep}"
            " || pcs cluster start --all --wait={sleep}\n"
            .format(sleep=ccspcmk2pcscmd.defs['pcscmd_start_wait'])
        )

from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
