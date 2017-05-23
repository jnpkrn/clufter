# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Filters for upgrading CIB formats"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter
from ..utils_xslt import xslt_params

from os.path import basename, splitext


@XMLFilter.deco('cib-1', 'cib-2')
def fmt_cib_1to2(flt_ctxt, in_obj):
    self = flt_ctxt.ctxt_wrapped
    validator_spec_min = self.out_format.etree_rng_validator_proper_specs()[0]
    if validator_spec_min:
        validator_spec_min = splitext(basename(validator_spec_min))[0]
    else:
        validator_spec_min = 'pacemaker-2.0'
    return (
        'etree',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            def_first=xslt_params(
                cib2_min_ver=validator_spec_min
            )
        )
    )
