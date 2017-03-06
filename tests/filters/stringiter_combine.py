# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `stringiter-combine*' filter(s)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
from .format import CompositeFormat
from .formats.string_iter import string_iter
from .utils_2to3 import str_enc

flt = 'stringiter-combine2'
stringiter_combine2 = FilterManager.init_lookup(flt).filters[flt]
#ccs = ccspcmk2pcscmd.in_format


class FiltersStringitercombineTestCase(TestCase):
    def testStringiterCombine2(self):
        result = stringiter_combine2(
            CompositeFormat(
                ('composite', ('stringiter', 'stringiter')),
                iter("ABC"), iter("DEF"),
                #"ABC", "DEF",
                formats=(string_iter, string_iter),
            )
        )
        #print(result.BYTESTRING())
        self.assertEquals(str_enc(result.BYTESTRING(), 'utf-8'),
                         '\n'.join("ABCDEF") + '\n')


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
