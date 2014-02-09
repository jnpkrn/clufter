# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Structured configuration formats such as corosync.conf"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import SimpleFormat


class simpleconfig(SimpleFormat):
    """"Structured configuration formats such as corosync.conf"""
    # yacc-based parser in fence-virt
    native_protocol = 'struct'

    @SimpleFormat.producing('bytestring')
    def get_bytestring(self, protocol):
        ret = super(Format, self).get_bytestring(self)
        if ret is not None:
            return ret

        # fallback
        # XXX TODO self('struct')
        raise NotImplementedError

    @SimpleFormat.producing('struct', protect=True)
    def get_struct(self, protocol):
        #return etree.fromstring(self('bytestring')).getroottree()
        pass
