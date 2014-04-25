# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing destilling XSLT from the sparse tree-organized snippets"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
from os.path import dirname, join
#from pprint import pprint

from lxml import etree

import _bootstrap  # known W402, required

from clufter.formats.ccs import ccs
from clufter.formats.coro import coroxml
from clufter.filter import XMLFilter

#WALK_DIR = join(dirname(dirname(__file__)), 'filters', 'cluster')
WALK_DIR = join(dirname(dirname(__file__)), 'filters')


class Ccs2NeedleXsltViewOnly(unittest.TestCase):
    def testXSLTTemplate2(self):
        flt = XMLFilter(ccs, coroxml)
        in_obj = ccs('file', join(dirname(__file__), 'filled.conf'))
        r = flt.get_template(in_obj, symbol='ccs2needlexml',
                             root_dir=WALK_DIR)

        ret = r if isinstance(r, list) else [r]
        print "\n".join([etree.tostring(i, pretty_print=True) for i in ret])

        assert not isinstance(r, list)


if __name__ == '__main__':
    unittest.main()
