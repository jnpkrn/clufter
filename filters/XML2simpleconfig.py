# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""xml2simpleconfig filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from clufter.filter import XMLFilter
from lxml import etree


@XMLFilter.deco('XML', 'simpleconfig')
def xml2simpleconfig(flt, in_obj, cmd_ctxt):
    for context in etree.iterwalk(in_obj('etree'), events=('start', 'end')):
        pass
    pass
