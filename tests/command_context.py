# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing command context"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from unittest import TestCase

from .command_context import CommandContextBase


class TestCommandContextBase(TestCase):
    def testAnabasisConstructor(self):
        ccb = CommandContextBase({'a': {'b': {'c': {'d': {'e': 42}}}}})
        e = ccb['a']['b']['c']['d']
        self.assertTrue(len(tuple(e.anabasis)) == 5)

    def testAnabasisBuilt(self):
        ccb = CommandContextBase()
        ccb['a'] =  {'b': {'c': {'d': {'e': 42}}}}
        e = ccb['a']['b']['c']['d']
        self.assertTrue(len(tuple(e.anabasis)) == 5)

    def testPreventedTaint(self):
        ccb = CommandContextBase({'a': 42})
        with ccb.prevented_taint():
            try:
                ccb['a'] = 43
            except RuntimeError:
                self.assertTrue(ccb['a'] == 42)
            else:
                self.assertTrue(False)
        try:
            ccb['a'] = 43
        except RuntimeError:
            self.assertTrue(False)
        else:
            self.assertTrue(ccb['a'] == 43)

    def testPreventedTaintTransitive(self):
        ccb = CommandContextBase({'a': {'b': 42}})
        with ccb.prevented_taint():
            try:
                ccb['a']['b'] = 43
            except RuntimeError:
                self.assertTrue(ccb['a']['b'] == 42)
            else:
                self.assertTrue(False)
        try:
            ccb['a']['b'] = 43
        except RuntimeError:
            self.assertTrue(False)
        else:
            self.assertTrue(ccb['a']['b'] == 43)


from os.path import join, dirname as d; execfile(join(d(__file__), '_gone'))
