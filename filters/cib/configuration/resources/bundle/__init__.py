# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....filters.cib2pcscmd import attrset_xsl
from ....utils_xslt import NL, xslt_is_member

cib2pcscmd_globaltags = (
    'network',
    'storage',
    'primitive',
)

cib2pcscmd_networkattrs = (
    'ip-range-start',
    'control-port',
    'host-interface',
    'host-netmask',
)

cib2pcscmd_portmapattrs = (
    'id',
    'port',
    'internal-port',
    'range',
)

cib2pcscmd_stmapattrs = (
    'id',
    'source-dir',
    'source-dir-root',
    'target-dir',
    'options',
)

cib2pcscmd = ('''\
    <xsl:choose>
        <xsl:when test="$pcscmd_extra_bundle">
''' + (
            verbose_inform('"new bundle: ", @id')
) + '''
            <xsl:value-of select="concat($pcscmd_pcs, 'resource bundle create ', @id,
                                         ' container ')"/>
            <xsl:for-each select="*[not(
''' + (
                xslt_is_member('name()', cib2pcscmd_globaltags)
) + ''')]">
                <xsl:choose>
        
                    <!-- skip the alleged container type duplications -->
                    <xsl:when test="position() != 1"/>
        
                    <!-- the nested snippets should be guarded with
                         xsl:when test="name() = 'foo'" -->
                    <clufter:descent-mix at="*"/>
        
                    <xsl:otherwise>
                        <xsl:message terminate="yes">
                            <xsl:value-of select="concat('WARNING: container type `',
                                                         name(), '` is currently',
                                                         ' unhandled')"/>
                        </xsl:message>
                    </xsl:otherwise>
        
                </xsl:choose>
            </xsl:for-each>
        
            <!-- network options -->
        
            <xsl:if test="network/@*[
 ''' + (
                xslt_is_member('name()', cib2pcscmd_networkattrs)
) + '''   
            ]">
                <xsl:value-of select="' network '"/>
            </xsl:if>
        
            <xsl:for-each select="network/@*">
                <xsl:choose>
                    <xsl:when test="
''' + (
                    xslt_is_member('name()', cib2pcscmd_networkattrs)
) + '''">
                        <xsl:value-of select='concat(" &apos;", name(), "=", ., "&apos;")'/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:message>
                            <xsl:value-of select="concat('WARNING: dropping non-whitelisted',
                                                         ' bundle/network option: `',
                                                         name(), '`')"/>
                        </xsl:message>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
        
            <!-- port-mapping options (possibly multi-spec) -->
        
            <xsl:for-each select="network/port-mapping">
                <xsl:if test="@*[
 ''' + (
                    xslt_is_member('name()', cib2pcscmd_portmapattrs)
) + '''   
                ]">
                    <xsl:value-of select="' port-map '"/>
                </xsl:if>
        
                <xsl:for-each select="@*">
                    <xsl:choose>
                        <xsl:when test="
''' + (
                        xslt_is_member('name()', cib2pcscmd_portmapattrs)
) + '''">
                            <xsl:value-of select='concat(" &apos;", name(), "=", ., "&apos;")'/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:message>
                                <xsl:value-of select="concat('WARNING: dropping non-whitelisted',
                                                             ' bundle/port-mapping option: `',
                                                             name(), '`')"/>
                            </xsl:message>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </xsl:for-each>
        
            <!-- storage-mapping options (possibly multi-spec) -->
        
            <xsl:for-each select="storage/storage-mapping">
                <xsl:if test="@*[
 ''' + (
                    xslt_is_member('name()', cib2pcscmd_stmapattrs)
) + '''   
                ]">
                    <xsl:value-of select="' storage-map '"/>
                </xsl:if>
        
                <xsl:for-each select="@*">
                    <xsl:choose>
                        <xsl:when test="
''' + (
                            xslt_is_member('name()', cib2pcscmd_stmapattrs)
) + '''">
                            <xsl:value-of select='concat(" &apos;", name(), "=", ., "&apos;")'/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:message>
                                <xsl:value-of select="concat('WARNING: dropping non-whitelisted',
                                                             ' bundle/storage-mapping option: `',
                                                             name(), '`')"/>
                            </xsl:message>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </xsl:for-each>

            <!-- meta attrs -->
            <xsl:choose>
                <xsl:when test="$pcscmd_extra_bundle_meta">
''' + (
                    attrset_xsl("meta_attributes", cmd='" meta"')
) + '''
                </xsl:when>
                <xsl:otherwise>
                    <xsl:message>%(bundle_meta_msg)s</xsl:message>
                </xsl:otherwise>
            </xsl:choose>

            <xsl:value-of select="'%(NL)s'"/>
''' + (
            verbose_ec_test
) + '''
        </xsl:when>
        <xsl:otherwise>
            <xsl:message>%(bundle_msg)s</xsl:message>
        </xsl:otherwise>
    </xsl:choose>
''') % dict(
    NL=NL,
    bundle_msg="WARNING: target pacemaker/pcs versions do not support"
               " `bundle` construct, hence omitted",
    bundle_meta_msg="WARNING: target pacemaker/pcs versions do not support"
                    " meta attributes for `bundle` construct, hence omitted",
)
