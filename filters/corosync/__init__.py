# -*- coding: UTF-8 -*-
# Copyright 2020 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

# following 2nd chance import is to allow direct usage context (testing, etc.)
try:
    from ....filters._2pcscmd import coro2pcscmd
except (ImportError, ValueError):
    from ...filters._2pcscmd import coro2pcscmd

needlexml2pcscmd = coro2pcscmd(node='', quorum='', totem='')
