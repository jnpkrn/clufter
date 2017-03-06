# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing XML helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase

from lxml import etree
from os.path import dirname, join

from .utils_xml import rng_pivot


class TestRngPivot(TestCase):
    def test_rng_pivot(self):
        #p = join(dirname_x(__file__, 2), 'formats', 'corosync', 'corosync.rng')
        p = join(dirname(__file__), 'corosync.rng')
        with open(p) as f:
            et = etree.parse(f)
        rng_pivot(et, 'logging')
        p = join(dirname(__file__), 'corosync.rng.exp')
        if False:  # to regenerate the expected file (manual review)
            with open(p, 'wb') as f:
                f.write(etree.tostring(et))
        else:
            with open(p, 'rb') as f:
                expected = f.read()
            self.assertEqual(etree.tostring(et), expected)


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
