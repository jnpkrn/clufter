# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cibprelude2cibcompact filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter


@XMLFilter.deco_xslt('cib-prelude', 'cib-compact')
class cibprelude2cibcompact: pass
