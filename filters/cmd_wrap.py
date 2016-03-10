# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
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

# man bash | grep -A2 '\s\+control operator$' (minus <newline>)
_CONTROL_OPERATORS = '||', '&', '&&', ';', ';;', '(', ')', '|', '|&'

def cmd_args_cutter(itemgroups):
    if not itemgroups:
        return itemgroups
    ret, acc = [], []
    cmd = itemgroups[0][0] if itemgroups[0] else ""
    for i in itemgroups:
        if len(i) > 1 and (not(i[0].startswith('-')) or i[0] == '-'):
            js = [e for e, j in enumerate(i) if e and j in _CONTROL_OPERATORS]
            if js:
                js.append(len(i))
                this_joint = 0
                for next_joint in js:
                    ret.extend(filter(bool, (tuple(acc), )))
                    acc = list(i[this_joint:next_joint])
                    this_joint = next_joint
                ret.append(tuple(acc))
                acc = []
            elif cmd.endswith('pcs'):
                pos = -1
                end = len(i)
                while pos + 1 < end:
                    pos += 1
                    # try to cut into "firm groups"
                    if pos <= end - 4:
                        if i[pos:pos + 2] in (("resource", "create"),
                                              ("stonith", "create")):
                            # "resource/stonith create X Y" firm group
                            ret.extend(
                                filter(bool, (tuple(acc), tuple(i[pos:pos + 4])))
                            )
                            pos += 4
                            acc = list(i[pos:pos])
                            pos += len(acc) - 1
                            continue
                    if pos <= end - 3:
                        if i[pos:pos + 2] in (('property', 'set'),
                                              ('property', 'unset')):
                            # "property set/unset non-option [non-option...]"
                            ret.extend(filter(bool, (tuple(acc), )))
                            acc = list(i[pos:pos + 2])
                            pos += len(acc) - 1
                            continue
                    if pos <= end - 2:
                        if i[pos] in ("op", "meta"):
                            # "op/meta non-option [non-option...]"
                            ret.extend(filter(bool, (tuple(acc), )))
                            acc = list(i[pos:pos + 1])
                            pos += len(acc) - 1
                            continue
                    # TBD
                    acc.append(i[pos])
                ret.append(tuple(acc))
                acc = []
            else:
                ret.extend((ii, ) for ii in i)
        elif cmd.endswith('pcs') and len(i) == 2 and i[0] == '--wait':
            # --wait NUM has to be reverted into --wait=NUM due to the
            # way pcs parser is "extended"
            ret.append(( '='.join(i), ))
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

    ret, continuation = [], []
    for line in in_obj('stringiter', protect_safe=True):
        if line.lstrip().startswith('#'):
            ret.extend(cw.wrap(line))
            continue
        # rough overapproximation of what is indeed a line continuation
        if line.endswith('\\') and not line.endswith('\\\\'):
            if '#' not in line:
                continuation.append(line[:-1])
                continue
            line += '\\'  # XXX
        line = ' '.join(continuation) + line
        continuation = []
        linecnt, rline, remains = -1, [], tw - 2  # ' \'
        itemgroups = cmd_args_cutter(command('bytestring', line)('separated'))
        itemgroups.reverse()
        while itemgroups:
            itemgroup = list(itemgroups.pop())
            itemgroup.reverse()
            while itemgroup:
                curlen = 0
                line = [itemgroup.pop()]
                curlen += len(line[-1])
                # best match fill
                while itemgroup \
                        and remains - (curlen + 1 + len(itemgroup[-1])) >= 0:
                    line.append(itemgroup.pop())
                    curlen += 1 + len(line[-1])
                # compensate for ' \' tail not necessary if very last item fits
                if not itemgroups and len(itemgroup) == 1 \
                        and len(itemgroup[-1]) == 1:
                    line.append(itemgroup.pop())
                    curlen += 1 + len(line[-1])
                # merge previous group to the current one if it fits the length
                if rline and not itemgroup \
                        and remains - (curlen + 1 + len(' '.join(rline))) >= 0 \
                        and (line[0] not in _CONTROL_OPERATORS
                             or not itemgroups or not itemgroups[-1]
                             or not itemgroups[-1][0]
                             or not itemgroups[-1][0][0] == '-'):
                    line = rline + line
                    rline = []
                    linecnt -= 1
                # second pass optionally handles the terminal propagation
                for i in xrange(2):
                    if rline:
                        tail = ' \\' if rline is not line else ''
                        rline = ' '.join(rline)
                        if not linecnt:
                            ret.append(rline + tail)
                            remains -= 2  # initial indent
                        else:
                            ret.append('  ' + rline + tail)
                    linecnt += 1
                    rline = line
                    if itemgroups or itemgroup:
                        break
    return ('stringiter', ret)
