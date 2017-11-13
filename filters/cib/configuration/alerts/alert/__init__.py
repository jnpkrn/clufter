# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....filters.cib2pcscmd import attrset_xsl
from ....utils_xslt import NL

cib2pcscmd = ('''\
    <!-- "pcs alert create" only supported with certain newer
         versions of pcs -->
    <xsl:variable name="AlertId" select="@id"/>
    <xsl:choose>
        <xsl:when test="$pcscmd_extra_alerts">
''' + (
            verbose_inform('"add alert listener: ", $AlertId')
) + '''
            <xsl:value-of select='concat($pcscmd_pcs, "alert create &apos;path=",
                                         @path, "&apos; id=", $AlertId)'/>
            <xsl:if test="@description">
                <xsl:value-of select='concat(" &apos;description=",
                                             @description, "&apos;")'/>
            </xsl:if>
''' + (
            attrset_xsl("instance_attributes", cmd='" options"')
            +
            attrset_xsl("meta_attributes", cmd='" meta"')
) + '''
            <xsl:value-of select="'%(NL)s'"/>
''' + (
            verbose_ec_test
) + '''
            <!-- select (CIB 2.10+)  -->
            <xsl:if test="select">
                <xsl:choose>
                    <xsl:when test="$pcscmd_extra_alerts_select">
                        <xsl:message>%(alerts_select_notimpl_msg)s</xsl:message>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:message>%(alerts_select_msg)s</xsl:message>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:if>

            <!-- recipients -->
            <xsl:for-each select="recipient">
''' + (
                verbose_inform('"add recipient for alert listener: ",'
                               ' @id, " for ", $AlertId')
) + '''
                <xsl:value-of select='concat($pcscmd_pcs, "alert recipient add ",
                                             $AlertId,
                                             " &apos;value=", @value, "&apos;",
                                             " id=", @id)'/>
                <xsl:if test="@description">
                    <xsl:value-of select='concat(" &apos;description=",
                                                 @description, "&apos;")'/>
                </xsl:if>
''' + (
                attrset_xsl("instance_attributes", cmd='" options"')
                +
                attrset_xsl("meta_attributes", cmd='" meta"')
) + '''
                <xsl:value-of select="'%(NL)s'"/>
''' + (
                verbose_ec_test
) + '''
            </xsl:for-each>

        </xsl:when>
        <xsl:otherwise>
            <xsl:message>%(alerts_msg)s</xsl:message>
        </xsl:otherwise>
    </xsl:choose>
''') % dict(
    NL=NL,
    alerts_msg="WARNING: target pacemaker/pcs versions do not support"
               " alerts, hence omitted",
    alerts_select_msg="WARNING: target pacemaker/pcs versions do not support"
                      " 'select' construct for alerts, hence omitted",
    alerts_select_notimpl_msg="WARNING: waiting for pcs to honor 'select'"
                              " construct for alerts in its syntax"
                              " (https://bugzilla.redhat.com/1512707)",
)
