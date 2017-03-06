# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing command context"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase

from .command_context import CommandContextBase


class TestCommandContextBase(TestCase):
    def testAnabasisConstructor(self):
        ccb = CommandContextBase({'a': {'b': {'c': {'d': {'e': 42}}}}})
        e = ccb['a']['b']['c']['d']
        self.assertEqual(len(tuple(e.anabasis)), 5)

    def testAnabasisBuilt(self):
        ccb = CommandContextBase()
        ccb['a'] =  {'b': {'c': {'d': {'e': 42}}}}
        e = ccb['a']['b']['c']['d']
        self.assertEqual(len(tuple(e.anabasis)), 5)

    def testPreventedTaint(self):
        ccb = CommandContextBase({'a': 42})
        with ccb.prevented_taint():
            try:
                ccb['a'] = 43
            except RuntimeError:
                self.assertEqual(ccb['a'], 42)
            else:
                self.assertTrue(False)
        try:
            ccb['a'] = 43
        except RuntimeError:
            self.assertTrue(False)
        else:
            self.assertEqual(ccb['a'], 43)

    def testPreventedTaintTransitive(self):
        ccb = CommandContextBase({'a': {'b': 42}})
        with ccb.prevented_taint():
            try:
                ccb['a']['b'] = 43
            except RuntimeError:
                self.assertEqual(ccb['a']['b'], 42)
            else:
                self.assertTrue(False)
        try:
            ccb['a']['b'] = 43
        except RuntimeError:
            self.assertTrue(False)
        else:
            self.assertEqual(ccb['a']['b'], 43)


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
