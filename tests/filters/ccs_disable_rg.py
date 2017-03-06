# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `ccs-disable-rg' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
flt = 'ccs-disable-rg'
ccs_disable_rg = FilterManager.init_lookup(flt).filters[flt]
ccs = ccs_disable_rg.in_format


class FiltersCcsDisableRGTestCase(TestCase):
    def testDisableRG(self):
        in_obj = ccs('file', join(dirname(dirname(__file__)), 'filled.conf'))
        ret = ccs_disable_rg(in_obj)
        #print(ret.BYTESTRING())
        disabled = bool(ret.ETREE().xpath("/cluster/rm/@disabled")[0])
        self.assertEquals(disabled, True)

from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
