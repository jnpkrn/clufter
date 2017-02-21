# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cmd-annotate filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from .. import package_name, version
from ..filter import Filter
from ..utils import args2tuple

from datetime import datetime
from sys import argv


cmd_annotate_self_id = ' '.join((package_name(), version))


@Filter.deco('Nothing', 'string-iter')
def cmd_annotate(flt_ctxt, in_obj):
    """Emit a comment block with clufter version + command used + target info"""
    ret = (''.join(('#', l)) for l in (
        (flt_ctxt['annotate_shell'], ) if 'annotate_shell' in flt_ctxt else ()
    ) + (
        " sequence generated on {0} with: {1}".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cmd_annotate_self_id,
        ),
        " invoked as: {0}".format(repr(argv)),
        " targeting system: {0}".format(
            repr(args2tuple(flt_ctxt['system'], *flt_ctxt['system_extra']))
        )
    ))
    return ('stringiter', ret)
