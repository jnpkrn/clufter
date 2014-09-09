# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""xml2simpleconfig filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter
from lxml import etree


@XMLFilter.deco('XML', 'simpleconfig')
def xml2simpleconfig(flt_ctxt, in_obj):
    """Mapping (almost bijective) XML -> simpleconfig

    Inverse mapping cannot be generally loseless, as XML cannot contain
    repeated attributes, which seems/is valid with simpleconfig.
    See `simpleconfig` docstring for details about the target representation.
    """
    # using similar trick of stack emulation in-place as command.analyse_chain.
    # but this is iterative rather than recursive :)
    root = []
    for action, e in etree.iterwalk(in_obj('etree'), events=('start', 'end')):
        if action == 'start':
            #print ">>> start", e.tag, root
            current = [e.tag, None, None]
            root.append(current)
            current[1] = tuple((n, v) for n, v in e.attrib.iteritems())
            #print "<<< start", e.tag, root
        elif action == 'end':
            #print ">>> end", e.tag, root
            if len(root) == 1:
                #assert id(e) == id(root)
                break
            current = root.pop()
            if root[-1][2] is None:
                root[-1][2] = []
            root[-1][2].append(current)
            #print "<<< end", e.tag, root
    return ('struct', root[-1])
