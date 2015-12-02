# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""XSLT helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from .utils_xml import NAMESPACES, XSL


NL = '&#xa;'


def xslt_identity(particular_selector=''):
    return '''\
    <xsl:template match="{0}@*|{0}node()"
                  xmlns:xsl="{1}">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
       </xsl:copy>
    </xsl:template>'''.format(particular_selector, NAMESPACES[XSL])


def xslt_is_member(item, items):
    """Readable item-itemset membership test"""
    items = "\n    '|" + "',\n    '|".join(items) + "',\n    '|'"
    return '''\
    (contains(concat({1}), concat('|', {0}, '|')))'''.format(item, items)


def xslt_boolean(param):
    """Return true/false value as understood within XSL templates"""
    return 'true()' if param else 'false()'


def xslt_params(**d):
    """Convert a provided dictionary into textual XSLT params"""
    ret = ""
    for k, v in d.iteritems():
        ret += '<xsl:param name="{0}" select="{1}"/>\n'.format(
            k, xslt_boolean(v) if isinstance(v, bool) else v
        )
    return ret


def xslt_id_friendly(inner):
    """Make the passed XPath expression yielding string XML ID friendly"""
    # XXX apostrophe missing
    return '''\
    translate(
        translate(
            {0},
            ' -/:',
            '____'
        ),
        '!&#x22;#$&#x25;&#x26;()*+,;&#x3c;=&#x3e;?@[\]^`{{|}}~',
        ''
    )'''.format(inner)


def xslt_string_mapping(d, what="."):
    """Convert dictionary into procedural mapping application (`xsl:when`s)"""
    ret = []
    for k, v in d.iteritems():
        if not isinstance(v, basestring):
            continue
        ret.append('''\
    <xsl:when test="{0} = '{1}'">'''.format(what, k))
        ret.append('''\
        <xsl:value-of select="'{0}'"/>'''.format(v))
        ret.append('''\
    </xsl:when>''')
    return '\n'.join(ret)
