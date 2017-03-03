# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Format representing merged/isolated (1/2 levels) of single command to exec"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from logging import getLogger
from shlex import split

log = getLogger(__name__)

from ..format import SimpleFormat
from ..protocol import Protocol
from ..utils import head_tail
from ..utils_2to3 import iter_items
from ..utils_func import add_item, apply_intercalate, apply_partition

# man bash | grep -A2 '\s\+metacharacter$'
_META_CHARACTERS =  '|', '&', ';', '(', ')', '<', '>' , ' ', '\t'
# man bash | grep -A2 '\s\+control operator$' (minus <newline>)
_CONTROL_OPERATORS = '||', '&', '&&', ';', ';;', '(', ')', '|', '|&'  # , '\n'
# man bash | grep -A4 '^RESERVED WORDS$' | tail -n1
_RESERVED_WORDS = ('!', 'case', 'coproc', 'do', 'done', 'elif', 'else', 'esac',
                   'fi', 'for', 'function', 'if', 'in', 'select', 'then',
                   'until', 'while', '{', '}', 'time', '[[', ']]')

_META_WORDS = _CONTROL_OPERATORS + _RESERVED_WORDS

ismetaword = \
    lambda x: \
    x in _META_WORDS \
        or x.endswith('(') and x[-2:-1] in '$<' \
            and x[:-2].rstrip(' \t') in ('', '"') \
        or x.startswith(')') and x[1:].lstrip(' \t') in ('', '"')


class command(SimpleFormat):
    native_protocol = SEPARATED = Protocol('separated')
    BYTESTRING = SimpleFormat.BYTESTRING
    DICT = Protocol('dict')
    MERGED = Protocol('merged')

    @staticmethod
    def _escape(base, qs=("'", '"')):
        # rule: last but one item in qs cannot be escaped inside enquotion
        # XXX: escaping _META_CHARACTERS
        ret = []
        for b in base:
            if any(c in b for c in qs + tuple(' \t#$')):
                use_q, prologue, epilogue = ('', ) * 3
                if not(b.endswith('(') and b[-2:-1] in '$<'
                       and b[:-2].rstrip(' \t') in ('', '"')
                       or
                       b.startswith(')') and b[1:].lstrip(' \t') in ('', '"')):
                    if b.startswith('<<<'):
                        _, prologue, b = b.partition('<<<')
                    use_qs = tuple(c for c in qs if c != "'") if '$' in b else qs
                    for q in use_qs:
                        if q not in b:
                            use_q = q
                            break
                    else:
                        use_q = use_qs[-1]
                        if use_q != qs[0]:
                            b = b.replace(use_q, '\\' + use_q)
                        else:
                            raise RuntimeError('cannot quote the argument')
                b = b.join((use_q, use_q)).join((prologue, epilogue))
            ret.append(b)
        return ret

    @SimpleFormat.producing(BYTESTRING, chained=True)
    def get_bytestring(self, *iodecl):
        """Return command as canonical single string"""
        # chained fallback
        return ' '.join(self.MERGED(protect_safe=True))

    @SimpleFormat.producing(SEPARATED, protect=True)
    def get_separated(self, *iodecl):
        merged = self.MERGED()
        merged.reverse()
        ret, acc, takes = [], [], 2  # by convention, option takes at most 1 arg
        while merged:
            i = merged.pop()
            # treat `-OPT` followed with `-NUMBER` just as if it was `NUMBER`,
            # also add an extra split on "meta words"
            if acc == ['--'] or i is None or ismetaword(i) \
                    or i.startswith('-') and i != '-' and not i[1:].isdigit():
                if not acc:
                    pass
                elif acc[0].startswith('-'):
                    ret.extend(filter(bool, (tuple(acc[:takes]),
                                             tuple(acc[takes:]))))
                else:
                    ret.append(tuple(acc))
                acc, takes = [] if i is None else [i], 2  # reset option-arg cnt
            elif self._dict.get('magic_split', False):
                split = i.split('::')  # magic "::"-split
                if len(acc) == 1 and acc[0].startswith('-') and acc[0] != '-':
                    takes = len(split) + 1  # sticky option multi-arguments
                acc.extend(split)
            else:
                acc.append(i)
            if acc and not merged:
                merged.append(None)  # mark terminal acc -> ret propagation
        return ret

    @SimpleFormat.producing(MERGED, protect=True)
    def get_merged(self, *iodecl):
        if self.BYTESTRING in self._representations:  # break the possible loop
            # XXX backticks not supported (yet)
            preprocessed = apply_partition(
                self.BYTESTRING(),
                lambda x, _, acc:
                    x == '(' and acc and not(acc[0].lstrip().startswith('#'))
                             and acc[-1][-1:] in '$<'
                             and not(any((
                                (lambda y, z: 0 if z == 1 and y == '"' else z % 2)(
                                    y, acc[-1].lstrip(' \t' + y).count(y) - acc[-1].count('\\' + y)
                                )
                             ) for y in "'\""))
                    or
                    x == ')' and acc and (not acc[-1] or acc[-1][-1] != '\\')
                             and any(y in acc[-2:-1] for y in '()')
                             and not(any((
                                acc[-1].lstrip(' \t' + y).count(y) - acc[-1].count('\\' + y)
                             ) % 2 for y in "'\""))
                    or
                    x == ';' and acc and not(acc[0].lstrip().startswith('#'))
                             and not(any((
                                acc[-1].lstrip(' \t' + y).count(y) - acc[-1].count('\\' + y)
                             ) % 2 for y in "'\""))
            )
            ret, prev = [], ''
            # XXX could check quotation pairs match using a stack
            for p in add_item(preprocessed, ''):
                tail1, tail2 = '', ''
                if p == '(':
                    if p == '(' and prev[-1:] in '$<':
                        qs = tuple(
                            x for x in '"' if
                            (prev[:-1].count(x) - prev[:-1].count('\\' + x)) % 2
                        )
                        if qs and prev[:-1].rstrip(" \t")[-1:] in qs:
                            prev, tail1, tail2 = prev.rpartition(qs[0])
                    ret.extend(filter(bool, split(prev) + [tail1 + tail2]))
                    ret[-1] += p
                    p = ''
                elif prev == ')':
                    qs = tuple(
                        x for x in '"' if
                        (p[:-1].count(x) - p[:-1].count('\\' + x)) % 2
                    )
                    if qs and p.lstrip(" \t")[:1] in qs:
                        tail1, tail2, p = p.partition(qs[0])
                    ret.extend(filter(bool, [prev + tail1 + tail2]))
                elif prev:
                    ret.extend(split(prev))
                prev = p
            if self._dict.get('enquote', True):
                ret = self._escape(ret)
            offset = 0
            for i, lexeme in enumerate(ret[:]):
                # heuristic(!) method to normalize: '-a=b' -> '-a', 'b'
                if (lexeme.count('=') == 1 and lexeme.startswith('-') and
                    ('"' not in lexeme or lexeme.count('"') % 2) and
                    ("'" not in lexeme or lexeme.count("'") % 2)):
                    ret[i + offset:i + offset + 1] = lexeme.split('=')
                    offset += 1
        elif self.DICT in self._representations:  # break the possible loop (2)
            d = self.DICT(protect_safe=True)
            if not isinstance(d, OrderedDict):
                log.warning("'{0}' format: not backed by OrderedDict".format(
                    self.__class__.name
                ))
            ret = list(d.get('__cmd__', ()))
            ret.extend((k, v) for k, vs in iter_items(d) for v in (vs or ((), ))
                                        if k not in ('__cmd__', '__args__'))
            ret.extend(d.get('__args__', ()))
        else:
            ret = self.SEPARATED(protect_safe=True)
        return apply_intercalate(ret)

    @SimpleFormat.producing(DICT, protect=True)
    # not a perfectly bijective mapping, this is a bit lossy representation,
    # on the other hand it canonicalizes the notation when turned to other forms
    def get_dict(self, *iodecl):
        separated = self.SEPARATED()
        separated.reverse()
        ret = OrderedDict()
        arg_bucket = '__cmd__'
        while separated:
            head, tail = head_tail(separated.pop())
            if head.startswith('-') and head != '-':
                arg_bucket = '__args__'
            else:
                head, tail = arg_bucket, head
            ret.setdefault(head, []).append(tail)
        return ret
