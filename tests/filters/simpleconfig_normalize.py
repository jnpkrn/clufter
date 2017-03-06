# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `simpleconfig-normalize' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
from .formats.simpleconfig import simpleconfig
from .utils_2to3 import str_enc

flt = 'simpleconfig-normalize'
simpleconfig_normalize = FilterManager.init_lookup(flt).filters[flt]


class FiltersSimpleconfigNormalizeTestCase(TestCase):
    def testSimpleconfigNormalize(self):
        result = simpleconfig_normalize(simpleconfig('struct',
            ('IGNORED',
            [],
            [('uidgid', [('uid', '0'), ('uid', '1000'), ('gid', '0')], [])])
        ))
        #print(result.BYTESTRING())
        self.assertEqual(str_enc(result.BYTESTRING(), 'utf-8'), """\
uidgid {
	uid: 0
	gid: 0
}
uidgid {
	uid: 1000
}
""")


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
