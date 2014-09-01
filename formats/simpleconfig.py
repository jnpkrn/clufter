# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Structured configuration formats such as corosync.conf"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import SimpleFormat
from ..protocol import Protocol
from ..utils import tuplist
from ..utils_func import apply_aggregation_preserving_depth


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
    def get_bytestring(self, protocol):
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
        indent, optindent = ('\t', ) * 2
        lbrace, rbrace, optsep = '{', '}', ': '
        # XXX previous apply_aggregation_preserving_passing_depth attempt
        #     was unsuccessful
        # XXX modulo trick seems not to help at all
        ret = apply_aggregation_preserving_depth(
            lambda xs:
                # string or terminal options passthrough
                xs
                if isinstance(xs, basestring)
                   or (isinstance(xs, tuple)
                       and len(xs) == 2 and not any(tuplist(x) for x in xs))
                else
                # joining terminal options (from previous passthrough)
                ('\n' + optindent).join(optsep.join(x)
                                        for x in ('',) + xs).lstrip('\n')
                if all(tuplist(x) for x in xs)  # and instance(xs, tuple)
                else
                # with braces-wrapping (using modulo arithmetics to shorten)
                ('\n').join((((len(l.split('#')) - 3) / 2 * '#' or '#'
                               + l[:len(l.split('#')) - 2])
                             + l[len(l.split('#')) - 2:])
                            #for x in tuple(xs[0:1]) + (lbrace,)
                            for x in tuple((xs[0] + ' ' + lbrace, ))
                                     + tuple(xs[1:]) + (rbrace, ) if x
                            for l in x.splitlines())
                if xs and not xs[0].startswith('#')  # and len(x) == 3
                else
                # without brace-wrapping (already wrapped, just shift right)
                ('\n').join((((len(l.split('#')) - 3) / 2 * '#' or '#'
                               + l[:len(l.split('#')) - 2])
                             + l[len(l.split('#')) - 2:])
                            for x in xs if x for l in x.splitlines())
        )(struct).replace('###', '').replace('##', indent)
        ret = '\n'.join(ret.splitlines()[1:-1]) + '\n'
        return ret

    @SimpleFormat.producing(STRUCT, protect=True)
    def get_struct(self, protocol):
        # TODO parsing struct from string
        raise NotImplementedError
