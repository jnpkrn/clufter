# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""pcs-resource-deps filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter
from ..utils import args2sgpl
from ..utils_cib import ResourceSpec
from ..utils_xslt import NL

def map_resource_to_pkgs(spec, *pkgs):
    pkgs = args2sgpl(pkgs)
    return (
        '<xsl:if test="' + ResourceSpec(spec).xsl_attrs_select + '">'
            '<xsl:value-of select="\'' + (NL.join(pkgs)) +  '\'"/>'
        '</xsl:if>'
    )


@XMLFilter.deco('pcs', 'string-list')
def pcs_resource_deps(flt_ctxt, in_obj):
    """Outputs set of logical dependencies based on configured resources"""
    return ('bytestring', flt_ctxt.ctxt_proceed_xslt(in_obj, textmode=True))
