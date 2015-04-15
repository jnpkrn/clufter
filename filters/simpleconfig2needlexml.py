# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""simpleconfig2needlexml filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import Filter


@Filter.deco('simpleconfig', 'coroxml-needle')
def simpleconfig2needlexml(flt_ctxt, in_obj):
    """Cooks XML representation of corosync.conf"""
    raise NotImplementedError("expected to come soon")
