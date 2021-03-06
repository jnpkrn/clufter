# -*- coding: UTF-8 -*-
# Copyright 2018 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase
from os.path import dirname, join
#from pprint import pprint

from lxml import etree

from .format import formats
formats = formats.plugins
from .formats.ccs import ccs
from .filter import XMLFilter
from .utils_2to3 import str_enc

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
        #print("\n".join([etree.tostring(i, pretty_print=True) for i in ret]))
        #print("\n".join([etree.tostring(i) for i in ret]))  # --> expected

        assert not isinstance(r, list)
        self.assertEqual(str_enc(etree.tostring(r, encoding='UTF-8'), 'utf-8'),
                         RESULT_DIRECT_XSLT)

    def testXSLTTemplate(self):
        flt = XMLFilter(formats)
        in_obj = ccs('file', join(dirname(__file__), 'filled.conf'))
        r = flt.get_template(in_obj, symbol='direct_xslt_test',
                             root_dir=WALK_DIR)

        assert not isinstance(r, list)
        et = in_obj('etree')
        #print(">>>", etree.tostring(et))
        #print(">>>", etree.tostring(r))
        modified = et.xslt(r)
        ret = str_enc(etree.tostring(modified, encoding='UTF-8'), 'utf-8')
        #print("<<<", ret)  # --> expected
        self.assertEqual(ret, RESULT_DIRECT_XSLT)


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
