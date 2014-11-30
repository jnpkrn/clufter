# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs-subst-nodes filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import FilterError, XMLFilter
from ..utils_cman import get_nodes

from logging import getLogger

log = getLogger(__name__)

@XMLFilter.deco('ccs', 'ccs')
def ccs_subst_nodes(flt_ctxt, in_obj):
    # could be in-situ, but stick with the default assumptions;
    # we temporarily store also the old name as <OLD>@<NEW> as name
    from copy import deepcopy

    self = flt_ctxt.ctxt_wrapped

    ret = deepcopy(in_obj('etree'))
    declared, existing = flt_ctxt['nodes'].split(' '), get_nodes(ret)
    declared_no, existing_no = map(len, (declared, existing))
    if declared_no != existing_no:
        raise FilterError(self, "number of provided node names does not match"
                                " the real configuration: {0} vs {1}"
                                .format(declared_no, existing_no))
    declared.reverse()
    for clusternode in existing:
        old, new = clusternode.attrib['name'], declared.pop()
        clusternode.attrib['name'] = '@'.join((old, new))
        log.info("substituted nodename: {0} -> {1}".format(old, new))

    # pick <OLD>@<NEW> naming from previous phase and run some implied
    # translations, dropping "<OLD>@" part along
    return ('etree', flt_ctxt.ctxt_proceed_xslt(type(in_obj)('etree', ret)))
