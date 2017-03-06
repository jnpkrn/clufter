# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `simpleconfig2needlexml' filter"""
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
from .utils_2to3 import bytes_enc

flt = 'simpleconfig2needlexml'
simpleconfig2needlexml = FilterManager.init_lookup(flt).filters[flt]


class FiltersSimpleconfig2NeedlexmlTestCase(TestCase):
    def testSimpleconfig2Needlexml(self):
        result = simpleconfig2needlexml(simpleconfig('struct',
            ('corosync-ONLY-INTERNAL-TAG-NOT-EXTERNALIZED-ANYWAY',
             [],
             [('totem', [('version', '2'), ('cluster_name', 'aus-cluster')], {}),
              ('nodelist',
               [],
               [('node', [('nodeid', '1'), ('ring0_addr', 'lolek.example.com')], []),
                ('node', [('nodeid', '2'), ('ring0_addr', 'bolek.example.com')], [])]),
              ('quorum',
               [('provider', 'corosync_votequorum'),
                ('expected_votes', '1'),
                ('two_node', '1')],
               [])])
        ))
        #print(result.BYTESTRING())
        self.assertEqual(result.BYTESTRING(), bytes_enc("""\
<corosync>
  <totem version="2" cluster_name="aus-cluster"/>
  <nodelist>
    <node nodeid="1" ring0_addr="lolek.example.com"/>
    <node nodeid="2" ring0_addr="bolek.example.com"/>
  </nodelist>
  <quorum provider="corosync_votequorum" expected_votes="1" two_node="1"/>
</corosync>
"""))


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
