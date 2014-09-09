# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing destilling XSLT from the sparse tree-organized snippets"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os.path as op; execfile(op.join(op.dirname(__file__), '_bootstrap.py'))


from unittest import TestCase
from os.path import dirname, join
#from pprint import pprint

from lxml import etree

from .filter import XMLFilter
from .format_manager import FormatManager
from .utils_prog import dirname_x

#WALK_DIR = join(dirname_x(__file__, 2), 'filters', 'cluster')
WALK_DIR = join(dirname_x(__file__, 2), 'filters')


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
        print "\n".join([etree.tostring(i, pretty_print=True) for i in ret])

        assert not isinstance(r, list)



execfile(op.join(op.dirname(__file__), '_bootstart.py'))
