# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing string_{iter,list,set} formats"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))

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


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
