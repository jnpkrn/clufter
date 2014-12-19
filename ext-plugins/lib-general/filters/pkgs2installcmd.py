# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""pkgs2installcmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import Filter
from ..facts import cmd_pkg_install


@Filter.deco('string-iter', 'command')
def pkgs2installcmd(flt_ctxt, in_obj):
    """Outputs installation command for packages on input"""
    return ('bytestring', cmd_pkg_install(in_obj('native', protect_safe=True),
                          flt_ctxt['system'], flt_ctxt['system_extra']) + '\n')
