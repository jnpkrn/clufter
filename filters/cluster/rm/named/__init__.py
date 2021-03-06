# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl


ccsflat2cibprelude = '''\
    <!--
        named ~ named (but only since resource-agents[named])
     -->
    <xsl:when test="name() = 'named' and $pcscmd_named_qual">
        <xsl:message terminate="yes">
            <xsl:value-of select="concat('Cannot convert named when the',
                                         ' target distro does not qualify: ',
                                         $pcscmd_named_qual)"/>
        </xsl:message>
    </xsl:when>
    <xsl:when test="name() = 'named'">
''' + (
        ResourceSpec('ocf:heartbeat:named').xsl_attrs
) + '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
''' + (
            rg2hb_xsl('named_config', 'config_file')
            +
            rg2hb_xsl('named_options')
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
    artefact_cond_ra('@config_file',
                     kind='A', desc='configuration file'),
))
