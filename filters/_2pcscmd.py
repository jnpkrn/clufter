# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""*2pcscmd filters helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from xml.sax.saxutils import escape

from ..utils_xslt import NL

verbose_prefix = ':: '
verbose_OK = verbose_prefix + 'OK'
verbose_FAILURE = verbose_prefix + 'FAILURE'

ec_test = "{0}{1}:{1}".format(
    escape("test $? -eq 0 && echo '{verbose_OK}' || echo '{verbose_FAILURE}'"
           .format(verbose_OK=verbose_OK, verbose_FAILURE=verbose_FAILURE),
           {"'": "&apos;", '"': "&quot;"}),
    NL
)

verbose_ec_test = '''\
    <xsl:if test="$pcscmd_verbose">
        <xsl:value-of select='"%(ec_test)s"'/>
    </xsl:if>
''' % dict(
    ec_test=ec_test
)

def verbose_inform(what):
    return '''\
    <xsl:if test="$pcscmd_verbose">
        <xsl:value-of select='concat("echo &apos;%(verbose_prefix)s",
                                     %(what)s,
                                     "&apos;%(NL)s")'/>
    </xsl:if>
''' % dict(
    what=what or '""',
    verbose_prefix=verbose_prefix or '""',
    NL=NL,
)
