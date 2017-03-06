# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `ccs-disable-rg' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
flt = 'ccs-disable-rg'
ccs_disable_rg = FilterManager.init_lookup(flt).filters[flt]
ccs = ccs_disable_rg.in_format


class FiltersCcsDisableRGTestCase(TestCase):
    def testDisableRG(self):
        in_obj = ccs('file', join(dirname(dirname(__file__)), 'filled.conf'))
        ret = ccs_disable_rg(in_obj)
        #print(ret.BYTESTRING())
        disabled = bool(ret.ETREE().xpath("/cluster/rm/@disabled")[0])
        self.assertEquals(disabled, True)

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
