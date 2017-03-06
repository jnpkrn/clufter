# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `cmd-wrap' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
from .formats.string_iter import string_iter
from .utils_2to3 import str_enc

flt = 'cmd-wrap'
cmd_wrap = FilterManager.init_lookup(flt).filters[flt]


class FiltersCmdWrapTestCase(TestCase):
    def testCmdWrap60(self):
        result = cmd_wrap(string_iter('stringiter', """\
# this is a long long long long long long long long, terribly long shell comment
/usr/bin/python setup.py saveopts -f setup.cfg pkg_prepare --editor=/usr/bin/vim
""".splitlines()
        ), text_width=60)
        #print(result.BYTESTRING())
        self.assertEqual(str_enc(result.BYTESTRING(), 'utf-8'), """\
# this is a long long long long long long long long,
# terribly long shell comment
/usr/bin/python setup.py saveopts -f setup.cfg pkg_prepare \\
  --editor /usr/bin/vim
""")

    def testCmdWrapCib2PcsCmd(self):
        result = cmd_wrap(string_iter('bytestring', """\
pcs -f tmp-cib.xml resource create RESOURCE-apache-webserver ocf:heartbeat:apache 'options= -Dwebserver' op stop 'id=RESOURCE-apache-webserver-OP-stop' 'name=stop' 'interval=0' 'timeout=122s'
"""), text_width=80)
        #print(result.BYTESTRING())
        self.assertEqual(str_enc(result.BYTESTRING()), """\
pcs -f tmp-cib.xml \\
  resource create RESOURCE-apache-webserver ocf:heartbeat:apache \\
  'options= -Dwebserver' \\
  op stop id=RESOURCE-apache-webserver-OP-stop name=stop interval=0 \\
  timeout=122s
""")


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
