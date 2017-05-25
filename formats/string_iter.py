# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Format representing a list of strings (new-line delimited)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import SimpleFormat
from ..protocol import Protocol
from ..utils_2to3 import bytes_enc, str_enc


class string_iter(SimpleFormat):
    native_protocol = BYTESTRINGITER = Protocol('bytestringiter')
    BYTESTRING = SimpleFormat.BYTESTRING

    @SimpleFormat.producing(BYTESTRING, chained=True)
    def get_bytestring(self, *iodecl):
        """Return command as canonical single string"""
        # chained fallback
        return (
            # add a trailing new-line as per conventions
            # XXX should there be a knob for that?
            bytes_enc(
                '\n'.join(str_enc(s, 'utf-8') for s
                          in self.BYTESTRINGITER(protect_safe=True) if s)
                + '\n',
                'utf-8'
            )
        )

    @SimpleFormat.producing(BYTESTRINGITER, protect=True)
    def get_bytestringiter(self, *iodecl):
        ret = (bytes_enc(s.strip(), 'utf-8')
               for s in (str_enc(self.BYTESTRING(), 'utf-8').rstrip('\n'))
                                                            .split('\n'))
        return ret


class string_list(string_iter):
    native_protocol = BYTESTRINGLIST = Protocol('bytestringlist')

    @SimpleFormat.producing(BYTESTRINGLIST, protect=True)
    def get_bytestringlist(self, *iodecl):
        return list(self.BYTESTRINGITER(protect_safe=True))


class string_set(string_iter):
    native_protocol = BYTESTRINGSET = Protocol('bytestringset')

    @SimpleFormat.producing(BYTESTRINGSET, protect=True)
    def get_bytestringset(self, *iodecl):
        return set(self.BYTESTRINGITER(protect_self=True))
