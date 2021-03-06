# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Test exercising _try_edit"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))

from os.path import dirname
from unittest import TestCase

from .filter_manager import FilterManager
from .utils_prog import getenv_namespaced, setenv_namespaced


class TryEdit(TestCase):
    def setUp(self):
        setenv_namespaced('NOSALT', 'true')
        self.flt_mgr = FilterManager.init_lookup('ccs2needlexml',
                                                 ext_plugins=False)

    #def tearDown(self):
    #    self.flt_mgr.registry.setup(True)  # start from scratch
    #    self.flt_mgr = None

    def test_fix_manually(self):
        testfile = join(dirname(__file__), 'try_edit.conf')
        out_obj = self.flt_mgr('ccs2needlexml', ('file', testfile),
                               editor="sed -i -e 's|-1|1|'")
                               #editor="sed -i 's|\-1|1|;w /dev/stdout' --")
        #print(out_obj('bytestring'))
        with open(join(dirname(__file__), 'try_edit.ok'), 'rb') as okfd:
            self.assertEqual(out_obj("bytestring"), okfd.read())


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
