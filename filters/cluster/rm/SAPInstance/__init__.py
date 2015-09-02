# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl


ccsflat2cibprelude = '''\
    <!--
        SAPInstance ~ SAPInstance
     -->
    <xsl:when test="name() = 'SAPInstance'">
''' + (
        ResourceSpec('ocf:heartbeat:SAPInstance').xsl_attrs
) + '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
''' + (
            rg2hb_xsl('InstanceName', req=True)
            +
            rg2hb_xsl('DIR_EXECUTABLE')
            +
            rg2hb_xsl('DIR_PROFILE')
            +
            rg2hb_xsl('START_PROFILE')
            +
            rg2hb_xsl('START_WAITTIME')
            +
            rg2hb_xsl('AUTOMATIC_RECOVER')
            +
            rg2hb_xsl('PRE_START_USEREXIT')
            +
            rg2hb_xsl('POST_START_USEREXIT')
            +
            rg2hb_xsl('PRE_STOP_USEREXIT')
            +
            rg2hb_xsl('POST_STOP_USEREXIT')
) + '''
        </instance_attributes>
    </xsl:when>
'''
