# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, xslt_is_member

# https://bugzilla.redhat.com/show_bug.cgi?id=1441332#c5
cib2pcscmd_id_whitelist = (
    'acl_role',
    'rsc_colocation',
    'rsc_location',
    'rsc_order',
    'rsc_ticket',
)

cib2pcscmd = ((
    verbose_inform('"new ACL role: ", @id')
) + '''
    <xsl:value-of select="concat($pcscmd_pcs, 'acl role create', ' ', @id)"/>
    <xsl:if test="@description != ''">
        <xsl:value-of select='concat(" &apos;description=", @description,
                                     "&apos;")'/>
    </xsl:if>
    <xsl:for-each select="acl_permission">
        <!-- XXX only allow a small amount of permissions to be in-line -->
        <xsl:choose>
            <xsl:when test="@xpath">
                <xsl:value-of select="concat(' ', @kind)"/>
                <xsl:value-of select='concat(" xpath &apos;", @xpath, "&apos;")'/>
            </xsl:when>
            <xsl:when test="@reference">
                <xsl:variable name="CibAclReferenced" select="//*[@id = current()/@reference]"/>
                <xsl:choose>
                    <xsl:when test="
''' + (
                        xslt_is_member('name($CibAclReferenced)', cib2pcscmd_id_whitelist)
) + '''">
                    <xsl:value-of select="concat(' ', @kind)"/>
                        <xsl:value-of select="concat(' id ', @reference)"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:message>
                            <xsl:value-of select="concat('WARNING: ACL: current pcs',
                                                         ' does not allow one to',
                                                         ' specify identifier with `',
                                                         name($CibAclReferenced),
                                                         '` element')"/>
                        </xsl:message>
                        <xsl:value-of select="concat(' ', @kind)"/>
                        <xsl:value-of select="concat(' id ', @reference)"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:when test="@object-type">
                <xsl:message>
                    <xsl:value-of select="concat('NOTE: ACL: current pcs can only',
                                                 ' express particular tag (optionally',
                                                 ' qualified with an attribute',
                                                 ' presence) as a subject of ACL',
                                                 ' within CIB indirectly with',
                                                 ' more complex XPath expression',
                                                 ' [https://bugzilla.redhat.com/1440890]')"/>
                </xsl:message>
                <xsl:value-of select="concat(' ', @kind)"/>
                <xsl:value-of select='concat(" xpath &apos;//", @object-type)'/>
                <xsl:if test="@attribute">
                    <xsl:value-of select="concat('[', @attribute, ']')"/>
                </xsl:if>
                <xsl:value-of select='"&apos;"'/>
            </xsl:when>
        </xsl:choose>
    </xsl:for-each>
    <xsl:value-of select="'%(NL)s'"/>
''' + (
    verbose_ec_test
)) % dict(
    NL=NL,
)
