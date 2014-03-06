# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2needlexml = '''\
    <node id="{@nodeid}" ring0_addr="{@name}"/>
'''

obfuscate_identifiers = '''\
    <xsl:copy>
        <xsl:copy-of select="@*"/>
        <xsl:attribute name="name">
            <!-- xsl:value-of select="concat('NODE-', @nodeid)"/ -->
            <xsl:value-of select="concat('NODE-', count())"/>
        </xsl:attribute>
    </xsl:copy>
'''

ccs2ccs_pcmk = '''\
    <clusternode name="{@name}" nodeid="${@nodeid}">
        <fence>
            <method name="pcmk-method">
                <device name="pcmk-redirect" port="{@name}"/>
            </method>
        </fence>
    </clusternode>
'''
