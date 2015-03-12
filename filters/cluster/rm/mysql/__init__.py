# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl

ccsflat2pcsprelude = '''\
    <!--
        mysql ~ mysql
     -->
    <xsl:when test="name() = 'mysql'">
''' + (
        ResourceSpec('ocf:heartbeat:mysql').xsl_attrs
) + '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
''' + (
            rg2hb_xsl('config', 'config_file')
) + '''\
            <!-- additional_parameters ~ listen_address + mysqld_options -->
            <xsl:if test="@listen_address or @mysqld_options">
            <nvpair id="{concat($Prefix, '-ATTRS-additional_parameters')}"
                    name="additional_parameters">
                <xsl:attribute name="value">
                    <xsl:if test="@listen_address">
                        <xsl:value-of select="concat(
                            '--bind-address=&quot;',
                            @listen_address,
                            '&quot; '
                        )"/>
                    </xsl:if>
                    <xsl:value-of select="@mysqld_options"/>
                </xsl:attribute>
            </nvpair>
            </xsl:if>
        </instance_attributes>
    </xsl:when>
'''

###

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@config_file',
                     kind='A', desc='configuration file'),
))
