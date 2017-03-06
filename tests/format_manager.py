# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing format manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase

from .format_manager import FormatManager
from .formats.ccs import ccs
from .formats.ccs import ccs_flat
from .formats.cib import cib
from .utils_2to3 import iter_items


class FormatManagerTestCase(TestCase):
    def setUp(self):
        self.fmt_mgr = FormatManager()

    def tearDown(self):
        self.fmt_mgr.registry.setup(True)  # start from scratch
        self.fmt_mgr = None


class Default(FormatManagerTestCase):
    def test_default(self):
        formats = self.fmt_mgr.formats
        #print(formats)
        for cls in ccs, ccs_flat, cib:
            self.assertTrue(cls.__name__ in formats)
            # the first was needed in the past, but now the more restrictive
            # one is ok
            self.assertEqual(type(cls), type(formats[cls.__name__]))
            self.assertEqual(cls, formats[cls.__name__])


class Injection(FormatManagerTestCase):

    def setUp(self):
        self.formats = {'frobniccs': ccs}
        self.fmt_mgr = FormatManager(paths=None, plugins=self.formats)

    def test_injection(self):
        formats = self.fmt_mgr.formats
        #print(formats)
        self.assertEqual(len(formats), len(self.formats))
        for fmt_id, fmt_cls in iter_items(self.formats):
            self.assertTrue(fmt_id in formats)
            self.assertEqual(fmt_cls, formats[fmt_id])


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
