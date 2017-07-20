# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing utils_prog module"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase

from .utils_prog import namever_partition


class UtilsProgFuncs(TestCase):
    """Test some functions from utils_prog"""

    def test_namever_partition(self):
        io_vals = (
            ("pacemaker-2.1",  ("pacemaker", 2, 1)),
            ("pacemaker-2.10", ("pacemaker", 2, 10)),
            ("pacemaker-2.18", ("pacemaker", 2, 18)),
            ("pacemaker-2.2",  ("pacemaker", 2, 2)),
        )
        for ival, oval in io_vals:
            self.assertEqual(namever_partition(ival), oval)


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
