# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `ccspcmk2pcscmd' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
flt = 'ccspcmk2pcscmd'
ccspcmk2pcscmd = FilterManager.init_lookup(flt).filters[flt]
ccs = ccspcmk2pcscmd.in_format


class FiltersCcspcmk2pcscmdTestCase(TestCase):
    def testConversion(self):
        in_obj = ccs('file', join(dirname(dirname(__file__)), 'filled.conf'))
        io_strings = (
            (('rhel', '7.1'),
            "pcs cluster setup --name test ju hele"
            " --consensus 200 --join 100 --token 5000"
            " --mcastport0 1002\n"
            "pcs cluster start --all && sleep {sleep}\n"
            .format(sleep=ccspcmk2pcscmd.defs['pcscmd_start_wait'])),
            (('rhel', '7.3'),
            "pcs cluster setup --name test ju hele"
            " --consensus 200 --join 100 --token 5000"
            " --mcastport0 1002\n"
            "pcs cluster start --all --wait={sleep}\n"
            .format(sleep=ccspcmk2pcscmd.defs['pcscmd_start_wait'])),
        )
        for system_extra, out_str in io_strings:
            ret = ccspcmk2pcscmd(in_obj, pcscmd_verbose=False,
                                         pcscmd_noauth=True,
                                         pcscmd_noguidance=True,
                                 system='linux', system_extra=system_extra)
            #print(ret.BYTESTRING())
            self.assertEqual(ret.BYTESTRING(), out_str)

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
