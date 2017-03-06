# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing CIB helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase

from .utils_cib import ResourceSpec

class TestResourceSpec(TestCase):
    def test_xsl_attrs_ocf(self):
        rs = ResourceSpec('ocf:heartbeat:Filesystem')
        self.assertEqual(rs.res_class, 'ocf')
        self.assertEqual(rs.res_provider, 'heartbeat')
        self.assertEqual(rs.res_type, 'Filesystem')

    def test_xsl_attrs_systemd(self):
        rs = ResourceSpec('systemd:smb')
        self.assertEqual(rs.res_class, 'systemd')
        self.assertEqual(rs.res_type, 'smb')


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
