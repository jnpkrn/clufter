# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@config_file',
                     kind='A', desc='configuration file'),
))

###

from ....utils_cib import ResourceSpec

ccsflat2pcsprelude = '''\
    <!--
        pgsql ~ postgres-8
     -->
    <xsl:when test="name() = 'postgres-8'">
''' + (
        ResourceSpec('ocf:heartbeat:pgsql').xsl_attrs
) + '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- config ~ config_file -->
            <nvpair id="{concat($Prefix, '-ATTRS-config')}"
                    name="config"
                    value="{@config_file}"/>
            <!-- start_opt ~ postmaster_options -->
            <xsl:if test="postmaster_options">
            <nvpair id="{concat($Prefix, '-ATTRS-start_opt')}"
                    name="start_opt"
                    value="{@postmaster_options}"/>
            </xsl:if>
            <!-- pgdba ~ postmaster_user -->
            <xsl:if test="postmaster_user">
            <nvpair id="{concat($Prefix, '-ATTRS-pgdba')}"
                    name="pgdba"
                    value="{@postmaster_user}"/>
            </xsl:if>
            <!-- XXX some items from postmaster_options could be
                 re-parsed into respective RA params
                 (-h $OCF_RESKEY_pghost) -->
        </instance_attributes>

        <!-- OPERATIONS -->
        <operations>
            <xsl:if test="@startup_wait">
            <op id="{concat($Prefix, '-OPS-start')}"
                name="start"
                interval="0"
                timeout="{concat(@startup_wait, 's')}"/>
            </xsl:if>
        </operations>
    </xsl:when>
'''
