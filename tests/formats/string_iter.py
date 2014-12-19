# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing string_{iter,list,set} formats"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))

from unittest import TestCase

from .format_manager import FormatManager
string_list = FormatManager.init_lookup('string-list').formats['string-list']


class FormatsStringIterTestCase(TestCase):
    def testBytestringToStringListSingle(self):
        sl = string_list('bytestring', "abcd")
        self.assertEqual(sl.STRINGLIST(), ['abcd'])
    def testBytestringToStringList(self):
        sl = string_list('bytestring', """\
a
b
c
b
a
""")
        self.assertEqual(sl.STRINGLIST(), ['a', 'b', 'c', 'b', 'a'])


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
