# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Format representing a list of strings (new-line delimited)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import SimpleFormat
from ..protocol import Protocol
from ..utils_2to3 import bytes_enc


class string_iter(SimpleFormat):
    native_protocol = STRINGITER = Protocol('stringiter')
    BYTESTRING = SimpleFormat.BYTESTRING

    @SimpleFormat.producing(BYTESTRING, chained=True)
    def get_bytestring(self, *iodecl):
        """Return command as canonical single string"""
        # chained fallback
        return (
            # add a trailing new-line as per conventions
            # XXX should there be a knob for that?
            bytes_enc(
                '\n'.join(s for s in self.STRINGITER(protect_safe=True) if s)
                + '\n',
                'utf-8'
            )
        )

    @SimpleFormat.producing(STRINGITER, protect=True)
    def get_stringiter(self, *iodecl):
        return (s.strip() for s in (self.BYTESTRING().rstrip('\n')).split('\n'))


class string_list(string_iter):
    native_protocol = STRINGLIST = Protocol('stringlist')

    @SimpleFormat.producing(STRINGLIST, protect=True)
    def get_stringlist(self, *iodecl):
        return list(self.STRINGITER(protect_safe=True))


class string_set(string_iter):
    native_protocol = STRINGSET = Protocol('stringset')

    @SimpleFormat.producing(STRINGSET, protect=True)
    def get_stringset(self, *iodecl):
        return set(self.STRINGITER(protect_self=True))
