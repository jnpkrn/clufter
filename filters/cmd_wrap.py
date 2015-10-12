# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cmd-wrap filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import Filter
from ..formats.command import command

from logging import getLogger
from os import getenv
from sys import maxint
from textwrap import TextWrapper

log = getLogger(__name__)


def cmd_args_cutter(itemgroups):
    if not itemgroups:
        return itemgroups
    ret, acc = [], []
    cmd = itemgroups[0][0] if itemgroups[0] else ""
    for i in itemgroups:
        if len(i) > 1 and (not(i[0].startswith('-')) or i[0] == '-'):
            if cmd.endswith('pcs'):
                pos = -1
                end = len(i)
                while pos + 1 < end:
                    pos += 1
                    if pos <= end - 2:
                        if i[pos] in ("op", "meta"):
                            ret.append(tuple(acc))
                            acc = [i[pos]]
                            continue
                    if pos <= end - 4:
                        if i[pos:pos + 2] == ("resource", "create"):
                            ret.extend((tuple(acc), tuple(i[pos:pos + 4])))
                            acc = []
                            pos += 3
                            continue
                    # TBD
                    acc.append(i[pos])
                ret.append(tuple(acc))
            else:
                ret.extend((ii, ) for ii in i)
        else:
            ret.append(i)
    return ret


@Filter.deco('string-iter', 'string-iter')
def cmd_wrap(flt_ctxt, in_obj):
    """Try to apply a bit smarter wrapping on lines carrying shell commands

    Smarter means:
    - standard textwrap module logic applied on comments splitting; otherwise:
    - do not delimit option from its argument
    - when line is broken vertically, append backslash for the continuation
      and indent subsequent lines for visual clarity
    - and as a side-effect: normalize whitespace occurrences

    Width used for rewrapping is based on three factors in precedence order:
    - text_width value inside the filter context (`flt_ctxt`)
      - 0 ~ fall-through to the value per the next item
      - -1 ~ apply no wrapping at all (mimicked by implying huge text_width)
      - positive ~ hard-limit the width (no smartness involved)
      - negative ~ high-limit the width, apply the inverse value only when not
                   exceeding the value per the next item
    - COLUMNS environmental variable, if defined and possesses integer value
    - hard-coded default of 72
    If absolute value at this point is lower than 20, fallback to 20.
    """
    try:
        tw_system = int(getenv('COLUMNS'))
    except TypeError:
        tw_system = 0
    try:
        tw = int(flt_ctxt.get('text_width'))
        if not tw:
            raise TypeError
        elif tw < -1:
            tw = -tw
            tw = tw if not tw_system or tw < tw_system else tw_system
        elif tw == -1:
            tw = maxint >> 1  # one order of magnitude less to avoid overflows
    except TypeError:
        tw = tw_system
    if tw < 20:  # watch out for deliberate lower limit
        tw = 20 if tw else 72
        log.info('Text width fallback: {0}'.format(tw))
    cw = TextWrapper(width=tw, subsequent_indent='# ')  # wrapper for comments

    ret = []
    for line in in_obj('stringiter', protect_safe=True):
        if line.lstrip().startswith('#'):
            ret.extend(cw.wrap(line))
            continue
        linecnt, rline, remains = 0, [], tw - 2  # ' \'
        itemgroups = cmd_args_cutter(command('bytestring', line)('separated'))
        for itemgroup in itemgroups:
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
