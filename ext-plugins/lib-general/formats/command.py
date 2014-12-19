# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Format representing merged/isolated (1/2 levels) of single command to exec"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from logging import getLogger

log = getLogger(__name__)

from ..format import SimpleFormat
from ..protocol import Protocol
from ..utils import head_tail
from ..utils_func import apply_intercalate


class command(SimpleFormat):
    native_protocol = SEPARATED = Protocol('separated')
    BYTESTRING = SimpleFormat.BYTESTRING
    DICT = Protocol('dict')
    MERGED = Protocol('merged')

    @SimpleFormat.producing(BYTESTRING, chained=True)
    def get_bytestring(self, *protodecl):
        """Return command as canonical single string"""
        # chained fallback
        return ' '.join(self.MERGED(protect_safe=True))

    @SimpleFormat.producing(SEPARATED, protect=True)
    def get_separated(self, *protodecl):
        ret = self.MERGED(protect_safe=True)
        newret, acc = [], []
        for i in ret:
            if i.startswith('-') and i != '-':
                if acc:
                    newret.append(tuple(acc))
                acc = [i]
            else:
                acc.append(i)
        # expect that, by convention, option takes at most a single argument
        newret.extend(filter(bool, (tuple(acc[:2]), tuple(acc[2:]))))
        return newret

    @SimpleFormat.producing(MERGED, protect=True)
    def get_merged(self, *protodecl):
        # try to look (indirectly) if we have "separated" at hand first
        if self.BYTESTRING in self._representations:  # break the possible loop
            from shlex import split
            ret = split(self.BYTESTRING())
            for i, lexeme in enumerate(ret[:]):
                # heuristic(!) method to normalize: '-a=b' -> '-a', 'b'
                if (lexeme.count('=') == 1 and
                    ('"' not in lexeme or lexeme.count('"') % 2) and
                    ("'" not in lexeme or lexeme.count("'") % 2)):
                    ret[i:i + 1] = lexeme.split('=')
        elif self.DICT in self._representations:  # break the possible loop (2)
            d = self.DICT(protect_safe=True)
            if not isinstance(d, OrderedDict):
                log.warning("'{0}' format: not backed by OrderedDict".format(
                    self.__class__.name
                ))
            ret = [(k, v) for k, v in d.iteritems() if k != '__args__']
            ret.extend(d.get('__args__', ()))
        else:
            ret = self.SEPARATED(protect_safe=True)
        return apply_intercalate(ret)

    @SimpleFormat.producing(DICT, protect=True)
    # not a perfectly bijective mapping, this is a bit lossy representation,
    # on the other hand, it canonicalize the notation when turned to other forms
    def get_dict(self, *protodecl):
        separated = self.SEPARATED()
        separated.reverse()
        ret = OrderedDict()
        while separated:
            head, tail = head_tail(separated.pop())
            head = head if head.startswith('-') and head != '-' else '__args__'
            acc = ret.setdefault(head, [])
            acc.append(tail)
        return ret
