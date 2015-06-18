# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Filter to disable RGManager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter


# avoid accidental start of rgmanager, see bz#723925;
# only rm tag already present as only then there is a chance
# of having RGManager + service set to start on boot
@XMLFilter.deco_xslt('ccs', 'ccs')
class ccs_disable_rg: pass
