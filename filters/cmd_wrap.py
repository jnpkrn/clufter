# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cmd-wrap filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import Filter
from ..formats.command import command, ismetaword
from ..utils_func import add_item
from ..utils_prog import FancyOutput

from collections import MutableMapping, defaultdict
from logging import getLogger
from os import getenv
from sys import maxint
from textwrap import TextWrapper

n, len_n = FancyOutput.normalized, FancyOutput.len_normalized
log = getLogger(__name__)

pcs_commands_hierarchy = {
    'cluster': {
        'auth': None,
        'setup': None,
        'start': None,
        'stop': None,
        'kill': None,
        'enable': None,
        'disable': None,
        'remote-node': {
            'add': None,
            'remove': None,
        },
        'status': None,
        'pcsd-status': None,
        'sync': None,
        'cib': None,
        'cib-push': None,
        'cib-upgrade': None,
        'edit': None,
        'node': {
            'add': None,
            'remove': None,
        },
        'uidgid': {
            None: None,
            'add': None,
            'rm': None,
        },
        'corosync': None,
        'reload': {
            'corosync': None,
        },
        'destroy': None,
        'verify': None,
        'report': None,
    },
    'resource': {
        None: None,
        'show': None,
        'list': None,
        'describe': None,
        'create': None,
        'delete': None,
        'enable': None,
        'disable': None,
        'restart': None,
        'debug-start': None,
        'debug-stop': None,
        'debug-promote': None,
        'debug-demote': None,
        'debug-monitor': None,
        'move': None,
        'ban': None,
        'clear': None,
        'standards': None,
        'providers': None,
        'agent': None,
        'update': None,
        'op': {
            'add': None,
            'remove': None,
            'defaults': None,
        },
        'meta': None,
        'group': {
            'add': None,
            'remove': None,
        },
        'ungroup': None,
        'clone': None,
        'unclone': None,
        'master': None,
        'manage': None,
        'unmanage': None,
        'defaults': None,
        'cleanup': None,
        'failcount': {
            'show': None,
            'reset': None,
        },
        'relocate': {
            'dry-run': None,
            'run': None,
            'show': None,
            'clear': None,
        },
        'utilization': None,
    },
    'stonith': {
        None: None,
        'show': None,
        'list': None,
        'describe': None,
        'create': None,
        'update': None,
        'delete': None,
        'cleanup': None,
        'level': {
            None: None,
            'add': None,
            'remove': None,
            'clear': None,
            'verify': None,
        },
        'fence': None,
        'confirm': None,
        'sbd': {
            'enable': None,
            'disable': None,
            'status': None,
            'config': None,
        },
    },
    'constraint': {
        None: None,
        'list': None,
        'show': None,
        'location': {
            None: None,
            'show': None,
            'remove': None,
        },
        'order': {
            None: None,
            'show': None,
            'set': None,
            'remove': None,
        },
        'colocation': {
            None: None,
            'show': None,
            'add': None,
            'set': None,
            'remove': None,
        },
        'ticket': {
            None: None,
            'show': None,
            'add': None,
            'set': None,
        },
        'remove': None,
        'ref': None,
        'rule': {
            'add': None,
            'remove': None,
        },
    },
    'property': {
        None: None,
        'list': None,
        'show': None,
        'set': None,
        'unset': None,
    },
    'acl': {
        None: None,
        'show': None,
        'enable': None,
        'disable': None,
        'role': {
            None: None,
            'create': None,
            'delete': None,
            'assign': None,
            'unassign': None,
        },
        'user': {
            None: None,
            'create': None,
            'delete': None,
        },
        'group': {
            None: None,
            'create': None,
            'delete': None,
        },
        'permission': {
            None: None,
            'add': None,
            'delete': None,
        },
    },
    'qdevice': {
        'status': None,
        'setup': {
            'model': None,
        },
        'destroy': None,
        'start': None,
        'stop': None,
        'kill': None,
        'enable': None,
        'disable': None,
    },
    'quorum': {
        None: None,
        'config': None,
        'status': None,
        'device': {
            'add': None,
            'remove': None,
            'status': None,
            'update': None,
        },
        'expected-votes': None,
        'unblock': None,
        'update': None,
    },
    'booth': {
        'setup': None,
        'destroy': None,
        'ticket': {
            'add': None,
            'remove': None,
            'grant': None,
        },
        'config': None,
        'create': {
            'ip': None,
        },
        'status': None,
        'pull': None,
        'sync': None,
        'enable': None,
        'disable': None,
        'start': None,
        'stop': None,
    },
    'status': {
        None: None,
        'resources': None,
        'groups': None,
        'cluster': None,
        'corosync': None,
        'quorum': None,
        'qdevice': None,
        'nodes': {
            None: None,
            'config': None,
            'corosync': None,
            'both': None,
        },
        'pcsd': None,
        'xml': None,
    },
    'config': {
        None: None,
        'show': None,
        'backup': None,
        'restore': None,
        'checkpoint': {
            None: None,
            'view': None,
            'restore': None,
        },
        'import-cman': None,
        'export': {
            'pcs-commands': None,
            'pcs-commands-verbose': None,
        },
    },
    'pcsd': {
        'certkey': None,
        'sync-certificates': None,
        'clear-auth': None,
    },
    'node': {
        'maintenance': None,
        'unmaintenance': None,
        'standby': None,
        'unstandby': None,
        'utilization': None,
    },
    'alert': {
        None: None,
        'config': None,
        'show': None,
        'create': None,
        'remove': None,
        'recipient': {
            'add': None,
            'update': None,
            'remove': None,
        },
    },
}


def cmd_args_colorizer_pcs(in_seq, color_map, initial=False,
                           level=pcs_commands_hierarchy):
    output = in_seq
    if len(in_seq) == 1 and initial and in_seq[0] == 'pcs':
        output = (in_seq[0].join((color_map['pcs'], color_map['restore'])), )
    else:
        output = []
        for i in add_item(in_seq, ''):
            if isinstance(level, MutableMapping):
                if i in level:
                    output.append(i)
                    level = level[i]
                    if level is None:
                        level = True
                    elif not isinstance(level, MutableMapping):
                        level = None  # XXX for the time being
                    continue  # need to yield new 'i' even if level is True
                level = None in level
            if level is True:
                last = len(output) - 1
                output = [ii.join((
                    color_map['subcmd'] if ee == 0 else '',
                    color_map['restore'] if ee == last else ''
                )) for (ee, ii) in enumerate(output)]
                level = None
            if i:
                output.append(i)
    return output


def cmd_args_cutter(itemgroups, color_map):
    if not itemgroups:
        return itemgroups

    ret, acc = [], []
    cmd = itemgroups[0][0] if itemgroups[0] else ""

    for e, i in enumerate(itemgroups):
        if len(i) and (not(i[0].startswith('-')) or i[0] == '-'):
            js = [f for f, j in enumerate(i) if ismetaword(j)]
            if js:
                js.extend((len(i), ) * 2)
                this_joint = 0
                for next_joint in js:
                    ret.extend(map(
                        lambda l: tuple(ii.join((
                            color_map['metaword'] if ismetaword(ii) else '',
                            color_map['restore'] if ismetaword(ii) else '',
                        )) for ee, ii in enumerate(l)),
                        filter(bool, (tuple(acc), ))
                    ))
                    acc = list(i[this_joint:next_joint])
                    this_joint = next_joint
            elif cmd.endswith('pcs'):
                pos = -1
                end = len(i)
                # separate and possibly colorize "pcs"
                if not e and i[0] == 'pcs':
                    ret.append(cmd_args_colorizer_pcs(i[0:1], color_map,
                                                      initial=True))
                    pos += 1
                while pos + 1 < end:
                    pos += 1
                    # try to cut into "firm groups"
                    if pos <= end - 4:
                        if i[pos:pos + 2] in (("resource", "create"),
                                              ("stonith", "create")):
                            # "resource/stonith create X Y" firm group
                            ret.extend(map(
                                lambda x: cmd_args_colorizer_pcs(x, color_map),
                                filter(bool, (tuple(acc), tuple(i[pos:pos + 4])))
                            ))
                            pos += 4
                            acc = list(i[pos:pos])
                            pos += len(acc) - 1
                            continue
                    if pos <= end - 3:
                        if i[pos:pos + 2] in (('property', 'set'),
                                              ('property', 'unset')):
                            # "property set/unset non-option [non-option...]"
                            ret.extend(map(
                                lambda x: cmd_args_colorizer_pcs(x, color_map),
                                filter(bool, (tuple(acc), ))
                            ))
                            acc = list(i[pos:pos + 2])
                            pos += len(acc) - 1
                            continue
                    if pos <= end - 2:
                        if i[pos] in ("op", "meta"):
                            # "op/meta non-option [non-option...]"
                            ret.extend(map(
                                lambda x: cmd_args_colorizer_pcs(x, color_map),
                                filter(bool, (tuple(acc), ))
                            ))
                            acc = list(i[pos:pos + 1])
                            pos += len(acc) - 1
                            continue
                    # TBD
                    acc.append(i[pos])
                ret.append(cmd_args_colorizer_pcs(acc, color_map))
                acc = []
            else:
                ret.extend((ii, ) for ii in i)
        elif cmd.endswith('pcs'):
            if len(i) == 2:
                if i[0] == '--wait':
                    # --wait NUM has to be reverted into --wait=NUM due to the
                    # way pcs parser is "extended"
                    i = ( '='.join(i), )
                elif i[0] == '-f':
                    i = (ii.join((
                        color_map['file'] if ee == 0 else '',
                        color_map['restore'] if ee == 1 else ''
                    )) for ee, ii in enumerate(i))
            ret.append(tuple(i))
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
    color_map = (dict(((k, FancyOutput.get_color(
                               FancyOutput.table.get('pcscmd_' + k, '')))
                       for k in ('comment', 'file', 'metaword', 'pcs', 'subcmd')),
                        restore=FancyOutput.colors['restore'])
                if flt_ctxt.get('color') else defaultdict(lambda: ''))

    ret, continuation = [], []
    for line in in_obj('stringiter', protect_safe=True):
        if line.lstrip().startswith('#'):
            lines = cw.wrap(line)
            last = len(lines) - 1
            ret.extend(l.join((
                color_map['comment'] if e == 0 else '',
                color_map['restore'] if e == last else ''
            )) for e, l in enumerate(lines))
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
        itemgroups = cmd_args_cutter(command('bytestring', line)('separated'),
                                     color_map=color_map)
        itemgroups.reverse()
        while itemgroups:
            itemgroup = list(itemgroups.pop())
            itemgroup.reverse()
            while itemgroup:
                curlen = 0
                line = [itemgroup.pop()]
                curlen += len_n(line[-1])
                # best match fill
                while itemgroup \
                        and remains - (curlen + 1 + len_n(itemgroup[-1])) >= 0:
                    line.append(itemgroup.pop())
                    curlen += 1 + len_n(line[-1])
                # compensate for ' \' tail not necessary if very last item fits
                if not itemgroups and len(itemgroup) == 1 \
                        and len_n(itemgroup[-1]) == 1:
                    line.append(itemgroup.pop())
                    curlen += 1 + len_n(line[-1])
                # merge previous group to the current one if it fits the length
                if (rline
                    and not itemgroup
                    and remains - (curlen + 1 + len_n(' '.join(rline))) >= 0
                    and (not itemgroups
                         or not itemgroups[-1]
                         or not itemgroups[-1][0]
                         or not n(itemgroups[-1][0])[0] == '-'
                         or not ismetaword(n(line[0]))
                         or len(itemgroups) == 1 or not itemgroups[-2]
                         or ismetaword(n(itemgroups[-2][0])))):
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
