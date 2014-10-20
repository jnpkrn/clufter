# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from .... import package_name

pcs2pcsfinal = ('''\
    <xsl:choose>
        <xsl:when test="not(@provider = '%(package_name)s'
                            and
                            starts-with(@type, 'temporary-'))">
            <xsl:copy>
                <xsl:copy-of select="@*|node()"/>
            </xsl:copy>
        </xsl:when>
    </xsl:choose>
''') % dict(package_name=package_name())
