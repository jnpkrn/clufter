# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2needlexml = '''\
    <node>
        <xsl:for-each select="@*">
            <xsl:variable name="attr_name">
                <xsl:choose>
                    <!-- @nodeid -> @nodeid (unchanged) -->
                    <xsl:when test="name() = 'nodeid'">
                        <xsl:value-of select="name()"/>
                    </xsl:when>
                    <!-- @name -> @ring0_addr -->
                    <xsl:when test="name() = 'name'">
                        <xsl:value-of select="'ring0_addr'"/>
                    </xsl:when>
                    <!-- @votes -> @quorum_votes -->
                    <xsl:when test="name() = 'votes'">
                        <xsl:value-of select="'quorum_votes'"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="''"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            <xsl:if test="$attr_name != ''">
                <xsl:attribute name="{$attr_name}">
                    <xsl:value-of select="."/>
                </xsl:attribute>
            </xsl:if>
        </xsl:for-each>
        <xsl:if test="altname/@name">
            <xsl:attribute name="ring1_addr">
                <xsl:value-of select="altname/@name"/>
            </xsl:attribute>
        </xsl:if>
    </node>
'''

ccs2ccs_pcmk = '''\
    <xsl:copy>
        <xsl:copy-of select="@*|altname"/>
        <!-- "unfence" section disappears, "fence" one enforced below -->
        <fence>
            <method name="pcmk-method">
                <device name="pcmk-redirect" port="{@name}"/>
            </method>
        </fence>
    </xsl:copy>
'''

# following could be omitted but keep it around if we ever need
# to add some node attributes in the future
ccsflat2pcsprelude = '''\
    <node id="{@nodeid}"
          uname="{@name}"
          type="member"
          />
'''
