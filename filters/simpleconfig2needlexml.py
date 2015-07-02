# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""simpleconfig2needlexml filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from lxml import etree

from ..filter import Filter
from ..utils import selfaware


@selfaware
def _simpleconfig2needlexml(me, element, options, sections):
    # must not attempt to modify anything from options/sections in-place
    element.attrib.update(options)
    element.extend([me(etree.Element(s[0]), *s[1:]) for s in sections])
    return element


@Filter.deco('simpleconfig-normalized', 'coroxml-needle')
def simpleconfig2needlexml(flt_ctxt, in_obj):
    """Cooks XML representation of corosync.conf"""
    struct = in_obj('struct', protect_safe=True)
    return ('etree', _simpleconfig2needlexml(etree.Element("corosync"),
                                             *struct[1:]))
