# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl


ccsflat2cibprelude = '''\
    <!--
        VirtualDomain ~ vm
     -->
    <xsl:when test="name() = 'vm'">
''' + (
        ResourceSpec('ocf:heartbeat:VirtualDomain').xsl_attrs
) + '''
        <!-- SHOW-STOPPERS -->
        <xsl:if test="@use_virsh = '0'">
            <xsl:message terminate="true"
            >Cannot reliably convert non-virsh configuration</xsl:message>
        </xsl:if>

        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- config ~ xmlfile -->
            <xsl:if test="@xmlfile or @path">
            <nvpair id="{concat($Prefix, '-ATTRS-config')}"
                    name="config"
                    value="{@xmlfile}">
                <xsl:if test="not(@xmlfile)">
                    <xsl:attribute name="value">
                        <!-- XXX simply assume the extension -->
                        <xsl:value-of select="concat(@path, '/', @name, '.xml')"/>
                    </xsl:attribute>
                </xsl:if>
            </nvpair>
            </xsl:if>
''' + (
            rg2hb_xsl('hypervisor', 'hypervisor_uri')
            +
            rg2hb_xsl('snapshot')
) + '''\
        </instance_attributes>
    </xsl:when>
'''

###

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@xmlfile',
                     kind='A', desc='libvirt XML domain definition'),
))
