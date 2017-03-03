# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""simpleconfig-normalize filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from logging import getLogger

log = getLogger(__name__)

from ..filter import Filter
from ..utils import selfaware
from ..utils_2to3 import iter_items


@selfaware
def _simpleconfig_normalize(me, parent_section):
    # must not attempt to modify anything from parent_section in-place
    parent_tag, parent_options, parent_sections = parent_section
    parent_sections_new = []
    for s in parent_sections:
        tag, options, sections = s
        opts = OrderedDict()
        for n, v in options:
            vals = opts.setdefault(n, [])
            if v in vals:
                log.warning("omitting duplicated `({0}, {1}}' option from"
                            " normalization".format(n, v))
            else:
                vals.append(v)
        options = []
        for n, vals in iter_items(opts):
            options.append((n, vals[0]))
            vals[:] = vals[1:]
        parent_sections_new.append((tag, options, [me(s) for s in sections]))
        for i, (n, vals) in enumerate((n, vals) for n, vals in iter_items(opts)
                                      if vals):
            if not i and sections:
                log.warning("current section `{0}' needs normalization but"
                            " contains subsections (not expected)".format(tag))
            for v in vals:
                parent_sections_new.append((tag, ((n, v), ), ()))
    return (parent_tag, parent_options, parent_sections_new)


@Filter.deco('simpleconfig', 'simpleconfig-normalized')
def simpleconfig_normalize(flt_ctxt, in_obj):
    """Normalizes simpleconfig per simpleconfig-normalized format description

    (Mentioned traversal is deliberately defined as post-order here.)
    """
    struct = in_obj('struct', protect_safe=True)
    return ('struct', _simpleconfig_normalize(struct))
