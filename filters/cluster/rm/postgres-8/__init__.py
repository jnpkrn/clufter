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

from ....utils_cib import ResourceSpec, rg2hb_xsl

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
''' + (
            rg2hb_xsl('config', 'config_file', req=True)
            +
            rg2hb_xsl('start_opt', 'postmaster_options')
            +
            rg2hb_xsl('pgdba', 'postmaster_user')
) + '''\
            <!-- XXX some items from postmaster_options could be
                 re-parsed into respective RA params
                 (-h $OCF_RESKEY_pghost) -->
        </instance_attributes>

        <!-- OPERATIONS -->
        <operations>
''' + (
            rg2hb_xsl('start', 'startup_wait', op=True)
) + '''\
        </operations>
    </xsl:when>
'''
