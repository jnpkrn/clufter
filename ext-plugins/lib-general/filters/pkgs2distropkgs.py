# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""pkgs2distropkgs filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import Filter
from ..facts import package
from ..utils import args2sgpl


@Filter.deco('string-iter', 'string-iter')
def pkgs2distropkgs(flt_ctxt, in_obj):
    """Outputs distro packages based on 'logical packages'"""
    ret = args2sgpl(tuple(in_obj('native', protect_safe=True)))
    return ('native', (package(i, flt_ctxt['system'], flt_ctxt['system_extra'])
                       for i in ret if i))
