# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing utils module"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from unittest import TestCase, main

import _bootstrap  # known W402, required

from clufter.utils import func_defaults_varnames


class FuncDefaultsVarnames(TestCase):
    """Test utils.func_defaults_varnames"""
    def _fnc(a, bar="ni"):
        pass

    def _gen(a, bar="ni"):
        yield

    def test_std_func(self):
        defaults, varnames = func_defaults_varnames(self._fnc)
        self.assertTrue("ni" in defaults.values())
        self.assertTrue('a' in varnames)
        self.assertTrue('bar' in varnames)
        self.assertEquals(len(varnames), 2)

    def test_std_func_skip(self):
        defaults, varnames = func_defaults_varnames(self._fnc, skip=1)
        self.assertTrue("ni" in defaults.values())
        self.assertTrue('bar' in varnames)
        self.assertEquals(len(varnames), 1)

    def test_generator(self):
        _, varnames = func_defaults_varnames(self._gen)
        self.assertEqual(len(varnames), 2)


if __name__ == '__main__':
    main()
