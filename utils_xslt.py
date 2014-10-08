# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""XSLT helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from .utils_xml import NAMESPACES


def xslt_identity(particular_selector=''):
    return '''\
    <xsl:template match="{0}@*|{0}node()"
                  xmlns:xsl="{1}">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
       </xsl:copy>
    </xsl:template>'''.format(particular_selector, NAMESPACES['xsl'])
