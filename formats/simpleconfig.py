# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Structured configuration formats such as corosync.conf"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import SimpleFormat
from ..protocol import Protocol
from ..utils_2to3 import basestring, bytes_enc, str_enc
from ..utils_func import apply_aggregation_preserving_passing_depth
from ..utils_prog import getenv_namespaced


class simpleconfig(SimpleFormat):
    """Structured configuration formats such as corosync.conf

    Internally ('struct'), it is structured liked this:

    SECTION  ::= tuple(TAG, OPTIONS, SECTIONS)  # [] tolerated, but fixed width
    SECTIONS ::= list-or-tuple(SECTION)
    OPTIONS  ::= list-or-tuple(OPTION)
    OPTION   ::= tuple(TAG, VALUE)  # must be tuple due to inner arragement
    TAG      ::= .*   # XXX and comment handling [^#@].*
    VALUE    ::= .*

    where SECTIONS form logical subsections (arbitrarily nested)

    Example:

    ('corosync-ONLY-INTERNAL-TAG-NOT-EXTERNALIZED-ANYWAY',
     [],
     [('totem', [('version', '2'), ('cluster_name', 'aus-cluster')], {}),
      ('nodelist',
       [],
       [('node', [('nodeid', '1'), ('ring0_addr', 'lolek.example.com')], []),
        ('node', [('nodeid', '2'), ('ring0_addr', 'bolek.example.com')], [])]),
      ('quorum',
       [('provider', 'corosync_votequorum'),
        ('expected_votes', '1'),
        ('two_node', '1')],
       [])])
    """
    # NOTE yacc-based parser in fence-virt
    native_protocol = STRUCT = Protocol('struct')
    BYTESTRING = SimpleFormat.BYTESTRING

    # notable lexical units for input
    lbrace_i, rbrace_i, optsep_i = '{',            '}',      ':'
    # notable lexical units for output (~ pretty-printing, hence with spaces)
    lbrace_o, rbrace_o, optsep_o = ' ' + lbrace_i, rbrace_i, optsep_i + ' '
    # same for input/output
    csep = '#'

    @SimpleFormat.producing(BYTESTRING)
    def get_bytestring(self, *iodecl):
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
        lbrace, rbrace, optsep = self.lbrace_o, self.rbrace_o, self.optsep_o
        ret = '\n'.join(
            apply_aggregation_preserving_passing_depth(
                lambda x, d:
                    # avoid IndexError
                    x if not x or not isinstance(x[0], basestring)
                    else
                    # OPTION
                    ((d - 3) // 2 * indent + x[0] + optsep + x[1], )
                        if isinstance(x, tuple) and len(x) == 2  # dif. SECTION
                    else
                    # rest ([''] at the end is for a final newline)
                    ([(d - 3) // 2 * indent + x[0] + lbrace] if d > 1 else [])
                        + list(xxxx for xx in filter(bool, x[1:])
                               for xxx in xx for xxxx in xxx)
                        + ([(d - 3) // 2 * indent + rbrace] if d > 1 else [''])
            )(struct)
        )
        return bytes_enc(ret, 'utf-8')

    @SimpleFormat.producing(STRUCT, protect=True)
    def get_struct(self, *iodecl):
        # similar to pcs.corosync_conf._parse_section (and Corosync itself)
        lbrace, rbrace, optsep = self.lbrace_i, self.rbrace_i, self.optsep_i
        csep = self.csep
        attrs, children = [], []
        work, t = [('', attrs, children)], str_enc(self.BYTESTRING(), 'utf-8')
        while t:
            h, t = t.split('\n', 1)
            if h.startswith(csep):
                continue
            elif lbrace in h:
                work.append((h.split(lbrace, 1)[0].strip(), [], []))
                attrs, children = work[-1][1:]
            elif rbrace in h:
                try:
                    cur = work.pop()
                    attrs, children = work[-1][1:]
                except IndexError:
                    raise RuntimeError("Unexpected closing brace")
                children.append(cur)
            elif optsep in h:
                attrs.append(tuple(x.strip() for x in h.split(optsep, 1)))
        ret = work.pop()
        if work:
            raise RuntimeError("Missing {0} closing brace(s)".format(len(work)))
        return ret


class simpleconfig_normalized(simpleconfig):
    """Structured configuration formats such as corosync.conf, normalized form

    Here, "normalized" is a synonym to "bijectively convertible to XML".
    Trivially, any elements-attributes XML is convertible to simpleconfig,
    but because simpleconfig can carry name-/key-duplicated options, something
    not suitable for reverse options-to-attributes mapping has to be normalized
    and because this is to serve in simpleconfig2needlexml filter (hence
    affecting only? uidgid entries), we define the normalization as follows:

    1. analyze current section whether it contains repeated options
      1a. no  -> goto 2. right away
      1b. yes -> for each duplicated option but without its value duplication
                 (in that case, such issue a warning), create a new
                 "following sibling" section and move the option here on its
                 own; if the current section contains subsection,
                 issue a warning about that
    2. continue with the next section in a defined traversal

    Fair enough, we've just described the simpleconfig-normalize filter :)
    """
    pass
