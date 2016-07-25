# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
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
                        <!-- xsl:value-of select="'quorum_votes'"/ -->
                        <xsl:value-of select="''"/>
                        <xsl:message>
                            <xsl:value-of select="concat('WARNING: node ',
                                                        ../@nodeid,
                                                        ' declared with ',
                                                        .,
                                                        ' vote(s), which is ')"/>
                                <xsl:choose>
                                    <xsl:when test="number(.) = 1">
                                        <xsl:value-of select="'a default anyway,'"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="concat('something not',
                                                                     ' 100% sane',
                                                                     ' nor advisable,')"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            <xsl:value-of select="concat(' hence not propagated (as',
                                                         ' `quorum_votes` property)')"/>
                        </xsl:message>
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
ccsflat2cibprelude = '''\
    <!-- differentiate between RHEL 6 and higher (rhbz#1207345) -->
    <node>
        <xsl:attribute name="id">
            <xsl:choose>
                <xsl:when test="$pcscmd_flatiron">
                    <!-- pacemaker + cman -->
                    <xsl:value-of select="@name"/>
                </xsl:when>
                <xsl:otherwise>
                    <!-- pacemaker + corosync/needle -->
                    <xsl:value-of select="@nodeid"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:attribute>
        <xsl:attribute name="uname">
            <xsl:value-of select="@name"/>
        </xsl:attribute>
        <xsl:attribute name="type">member</xsl:attribute>
    </node>
'''

###

ccspcmk2pcscmd = '''\
    <xsl:value-of select="concat(' ', @name)"/>
    <xsl:if test="altname/@name">
        <xsl:value-of select="concat(',', altname/@name)"/>
    </xsl:if>
'''
