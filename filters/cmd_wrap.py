# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cmd-wrap filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import Filter
from ..formats.command import command

from os import getenv
from textwrap import TextWrapper


@Filter.deco('string-iter', 'string-iter')
def cmd_wrap(flt_ctxt, in_obj):
    """Try to apply a bit smarter wrapping on lines carrying shell commands

    Smarter means:
    - do not delimit option from its argument
    - when line is broken vertically, append backslash for the continuation
      and indent subsequent lines for visual clarity
    - and as a side-effect: normalize whitespace occurrences
    """
    try:
        tw_system = int(getenv('COLUMNS'))
    except TypeError:
        tw_system = 0
    try:
        tw = int(flt_ctxt.get('text_width'))
        if not tw:
            raise TypeError
        elif tw < 0:
            tw = -tw
            tw = tw if not tw_system or tw < tw_system else tw_system
    except TypeError:
        tw = tw_system
    if not tw:
        tw = 72
    cw = TextWrapper(width=tw, subsequent_indent='# ')  # wrapper for comments

    ret = []
    for line in in_obj('stringiter', protect_safe=True):
        if line.lstrip().startswith('#'):
            ret.extend(cw.wrap(line))
            continue
        linecnt, rline, remains = 0, [], tw - 2  # ' \'
        for itemgroup in command('bytestring', line)('separated'):
            item = ' '.join(itemgroup)
            fills = len(item) + (1 if rline else 0)
            # also deal with text width overflow on the first line
            if (remains - fills >= 0 or not rline):
                rline.append(item)
                remains -= fills
            else:
                ret.append(('  ' if linecnt else '') + ' '.join(rline) + ' \\')
                linecnt += 1
                rline, remains = [item], tw - len(item) - 4  # ' \' & ident
        ret.append(('  ' if linecnt else '') + ' '.join(rline))
    return ('stringiter', ret)
