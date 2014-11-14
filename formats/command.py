# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Format representing merged/isolated (1/2 levels) of single command to exec"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import SimpleFormat
from ..protocol import Protocol
from ..utils_func import apply_intercalate


class command(SimpleFormat):
    native_protocol = SEPARATED = Protocol('separated')
    BYTESTRING = SimpleFormat.BYTESTRING
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
            return split(self.BYTESTRING())
        return apply_intercalate(self.SEPARATED(protect_safe=True))
