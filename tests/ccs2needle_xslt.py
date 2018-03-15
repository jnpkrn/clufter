# -*- coding: UTF-8 -*-
# Copyright 2018 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing destilling XSLT from the sparse tree-organized snippets"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase
from os.path import dirname, join
from sys import modules

from lxml import etree

from .filter import XMLFilter
from .format_manager import FormatManager
from .utils_2to3 import str_enc

WALK_DIR = join(dirname(modules[XMLFilter.__module__].__file__), 'filters')

class Ccs2NeedleXsltViewOnly(TestCase):
    def setUp(self):
        self.fmt_mgr = fmt_mgr = FormatManager()
        self.formats = fmt_mgr.plugins

    def tearDown(self):
        self.fmt_mgr.registry.setup(True)

    def testXSLTTemplate2(self):
        formats = self.formats
        flt = XMLFilter(formats)
        in_obj = formats['ccs']('file', join(dirname(__file__), 'filled.conf'))
        r = flt.get_template(in_obj, symbol='ccs2needlexml', root_dir=WALK_DIR)
        ret = r if isinstance(r, list) else [r]
        print("\n".join(str_enc(etree.tostring(i, encoding='UTF-8',
                                               pretty_print=True), 'utf-8')
                        for i in ret))

        assert not isinstance(r, list)


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
