# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2flatironxml = ccs2needlexml = ccs2coroxml = '''\
    <node id="{@nodeid}" ring0_addr="{@name}"/>
'''

aobfuscate_identifiers = '''\
    <xsl:copy>
        <xsl:copy-of select="@*"/>
        <xsl:attribute name="name">
            <!-- xsl:value-of select="concat('NODE-', @nodeid)"/ -->
            <xsl:value-of select="concat('NODE-', count())"/>
        </xsl:attribute>
    </xsl:copy>
'''
