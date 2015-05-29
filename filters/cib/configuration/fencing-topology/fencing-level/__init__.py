# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL

cib2pcscmd = ('''\
''' + (
    verbose_inform('"new stonith level: ", @index')
) + '''
    <xsl:value-of select='concat("pcs stonith level add",
                                 " ", @index,
                                 " ", @target,
                                 " &apos;", @devices, "&apos;")'/>
    <xsl:value-of select="'%(NL)s'"/>
''' + (
    verbose_ec_test
) + '''
''') % dict(
    NL=NL,
)
