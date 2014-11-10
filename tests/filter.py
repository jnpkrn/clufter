# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from unittest import TestCase
from os.path import dirname, join
#from pprint import pprint

from lxml import etree

from .format import formats
formats = formats.plugins
from .formats.ccs import ccs
from .filter import XMLFilter

WALK_DIR = join(dirname(__file__), 'XMLFormat-walk')

RESULT_TRAVERSE = \
    ('clusternodes-traverse_test', 'element: clusternodes', [
        ('clusternode-traverse_test', 'element: clusternode', [
        ]),
        ('clusternode-traverse_test', 'element: clusternode', [
        ])
    ])

RESULT_DIRECT_XSLT = \
    '<test version="1"><node>ju</node><node>hele</node></test>'


def fnc(symbol, elem, children):
    return symbol, "element: " + elem.tag, children.values()


class XMLTraverse(TestCase):
    def testDirectXSLT(self):
        flt = XMLFilter(formats)
        in_obj = ccs('file', join(dirname(__file__), 'filled.conf'))
        r = flt.proceed_xslt(in_obj, symbol='direct_xslt_test',
                             root_dir=join(dirname(__file__), 'XMLFormat-walk'))

        #ret = r if isinstance(r, list) else [r]
        #print "\n".join([etree.tostring(i, pretty_print=True) for i in ret])
        #print "\n".join([etree.tostring(i) for i in ret])  # --> expected

        assert not isinstance(r, list)
        self.assertTrue(etree.tostring(r) == RESULT_DIRECT_XSLT)

    def testXSLTTemplate(self):
        flt = XMLFilter(formats)
        in_obj = ccs('file', join(dirname(__file__), 'filled.conf'))
        r = flt.get_template(in_obj, symbol='direct_xslt_test',
                             root_dir=WALK_DIR)

        assert not isinstance(r, list)
        et = in_obj('etree')
        #print ">>>", etree.tostring(et)
        #print ">>>", etree.tostring(r)
        modified = et.xslt(r)
        ret = etree.tostring(modified)
        #print "<<<", ret  # --> expected
        self.assertTrue(ret == RESULT_DIRECT_XSLT)


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
