# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs_artefacts filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..filter import XMLFilter


def artefact(xpath, kind='?', own=False, desc=''):
    return '''\
    <xsl:value-of select="concat('{kind}; {own}; ', {xpath}, '; {desc}', '&#xA;')"/>
'''.format(xpath=xpath, kind=kind, own='1' if own else '0', desc=desc)


def artefact_cond(cond, xpath=None, **kwargs):
    if xpath is None:
        xpath = '.'
    return '''\
    <xsl:for-each select="{cond}">
        {artefact}</xsl:for-each>
'''.format(cond=cond, artefact=artefact(xpath, **kwargs))

def artefact_cond_ra(*args, **kwargs):
    kwargs['desc'] = nested_concat('RA/${name(..)}: ' + kwargs.get('desc'))
    return artefact_cond(*args, **kwargs)


def nested_concat(*args, **kwargs):
    """Make a concat body of argument(s) of strings and ${XSLT expressions}

    Keyword arguments:
        proper_nesting: whether initial and trailing quote is put externally

    Needlessly careless: produces too many extraneous empty strings ('').
    """
    proper_nesting = kwargs.get('proper_nesting', True)
    acc, part = '', ('', '', '}' + ''.join(args))
    while part[2]:
        if part[0]:
            acc += "', '" + part[0]
        xslt = part[2][:part[2].find('}')]
        if xslt:
            acc += "', " + xslt + ", '"
        part = part[2][len(xslt)+1:].partition("${")
    acc += part[0]
    return acc if proper_nesting else acc.join("''")


@XMLFilter.deco('ccs', 'SimpleFormat')
def ccs_artefacts(flt_ctxt, in_obj):
    """Outputs CVS-like file (kind; own; id; description) for CCS artefacts

    Note that "CCS artefacts" refers to any notable file/port/system-wide user,
    etc.  Boolean flag "own" is used to distinguish the assets/something
    provided (exposed) by the cluster stack itself and the artefacts being
    merely consumed.

    Kind can be:
        A   administrative file (mostly synonym to "application-specific
                                 configuration")
        C   command (binary, optionally with full path and arguments)
        D   directory
        F   general file
        I   IP address
        L   log file
        S   sensitive file
        X   executable file (binary or script with shebang)
    (perhaps also:
        G   group
        P   port (optionally suffixed with '[{tcp,udp}]'?)
        U   user
    )
    """
    return ('bytestring', flt_ctxt.ctxt_proceed_xslt(in_obj, textmode=True))
