# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl


ccsflat2pcsprelude = '''\
    <!--
        apache ~ apache
     -->
    <xsl:when test="name() = 'apache'">
''' + (
        ResourceSpec('ocf:heartbeat:apache').xsl_attrs
) + '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
''' + (
            rg2hb_xsl('configfile', 'config_file')
) + '''\
            <!-- options ~ httpd_options (if present; + name, server_root) -->
            <nvpair id="{concat($Prefix, '-ATTRS-options')}"
                    name="options">
                <xsl:attribute name="value">
                    <xsl:value-of select="concat(
                        ' -D', @name
                    )"/>
                    <xsl:if test="@server_root">
                        <xsl:value-of select="concat(
                            ' -d &quot;', @server_root, '&quot;'
                        )"/>
                    </xsl:if>
                    <xsl:if test="@httpd_options">
                        <xsl:value-of select="concat(
                            ' ', @httpd_options
                        )"/>
                    </xsl:if>
                </xsl:attribute>
            </nvpair>
''' + (
            # see rhbz#952132
            rg2hb_xsl('httpd', 'httpd')
) + '''\
        </instance_attributes>

        <!-- OPERATIONS -->
        <operations>
''' + (
            rg2hb_xsl('stop', 'shutdown_wait', op=True)
) + '''\
        </operations>
    </xsl:when>
'''

###

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@httpd',
                     kind='B', desc='path to httpd binary'),
    artefact_cond_ra('@server_root',
                     kind='D', desc='ServerRoot'),
    artefact_cond_ra('@config_file[../@server_root]',
                     xpath="concat(../@server_root, '/', .)",
                     kind='A', desc='configuration file'),
))
