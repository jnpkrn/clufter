# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing destilling XSLT from the sparse tree-organized snippets"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from unittest import TestCase
from os.path import dirname, join
from sys import modules

from lxml import etree

from .filter import XMLFilter
from .format_manager import FormatManager

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
        print("\n".join((etree.tostring(i, encoding='unicode', pretty_print=True)
                         for i in ret)))

        assert not isinstance(r, list)


from os.path import join, dirname as d; execfile(join(d(__file__), '_gone'))
