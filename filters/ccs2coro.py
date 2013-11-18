# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from clufter.filter import XMLFilter
#from lxml import etree


@XMLFilter.deco('ccs', 'coroxml')
def ccs2coroxml(flt, in_obj):
    #print etree.tostring(in_obj('etree').xslt(flt.get_template(in_obj)))
    return ('etree', flt.proceed_xslt(in_obj))
