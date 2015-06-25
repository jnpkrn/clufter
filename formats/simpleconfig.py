# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Structured configuration formats such as corosync.conf"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import SimpleFormat
from ..protocol import Protocol
from ..utils_func import apply_aggregation_preserving_passing_depth
from ..utils_prog import getenv_namespaced


class simpleconfig(SimpleFormat):
    """"Structured configuration formats such as corosync.conf

    Internally ('struct'), it is structured liked this:

    SECTION  ::= list-or-tuple(TAG, OPTIONS, SECTIONS)
    SECTIONS ::= list(SECTION)  # must be list due to arragement
    OPTIONS  ::= tuple(OPTION)  # must be tuple (ditto)
    OPTION   ::= list-or-tuple(TAG, VALUE)
    TAG      ::= [^#@].*        # due to arrangement
    VALUE    ::= .*

    where SECTIONS form logical subsections (arbitrarily nested)

    Example:

    ('corosync-ONLY-INTERNAL-TAG-NOT-EXTERNALIZED-ANYWAY',
     (),
     [['totem', (('version', '2'), ('cluster_name', 'aus-cluster')), None],
      ['nodelist',
       (),
       [['node', (('id', '1'), ('ring0_addr', 'lolek.example.com')), None],
        ['node', (('id', '2'), ('ring0_addr', 'bolek.example.com')), None]]],
      ['quorum',
       (('provider', 'corosync_votequorum'),
        ('expected_votes', '1'),
        ('two_node', '1')),
       None]])
    """
    # NOTE yacc-based parser in fence-virt
    native_protocol = STRUCT = Protocol('struct')
    BYTESTRING = SimpleFormat.BYTESTRING

    @SimpleFormat.producing(BYTESTRING)
    def get_bytestring(self, *protodecl):
        """Externalize 'struct', that is basically, pretty print it

        For example above, the result is something like:

        totem {
            version: 2
            cluster_name: aus-cluster
        }
        nodelist {
            node {
                id: 1
                ring0_addr: lolek.example.com
            }
            node {
                id: 2
                ring0_addr: bolek.example.com
            }
        }
        quorum {
            provider: corosync_votequorum
            expected_votes: 1
            two_node: 1
        }
        """
        # try to look (indirectly) if we have a file at hand first
        ret = super(simpleconfig, self).get_bytestring(self.BYTESTRING)
        if ret is not None:
            return ret

        # fallback
        struct = self.STRUCT(protect_safe=True)
        indent, optindent = (getenv_namespaced('COROINDENT', '\t'), ) * 2
        lbrace, rbrace, optsep = ' {', '}', ': '  # spaces intentional
        ret = '\n'.join(
            apply_aggregation_preserving_passing_depth(
                lambda x, d:
                    # avoid IndexError
                    x if not x or not isinstance(x[0], basestring)
                    else
                    # OPTION
                    ((d - 3) / 2 * indent + x[0] + optsep + x[1], )
                        if isinstance(x, tuple) and len(x) == 2  # dif. SECTION
                    else
                    # rest
                    ([(d - 3) / 2 * indent + x[0] + lbrace] if d > 1 else [])
                        + list(xxxx for xx in filter(bool, x[1:])
                               for xxx in xx for xxxx in xxx)
                        + ([(d - 3) / 2 * indent + rbrace] if d > 1 else [])
            )(struct)
        )
        return ret

    @SimpleFormat.producing(STRUCT, protect=True)
    def get_struct(self, *protodecl):
        # TODO parsing struct from string
        raise NotImplementedError
