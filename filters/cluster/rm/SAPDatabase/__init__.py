# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl


ccsflat2cibprelude = '''\
    <!--
        SAPDatabase ~ SAPDatabase
     -->
    <xsl:when test="name() = 'SAPDatabase'">
''' + (
        ResourceSpec('ocf:heartbeat:SAPDatabase').xsl_attrs
) + '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
''' + (
            rg2hb_xsl('SID', req=True)
            +
            rg2hb_xsl('DBTYPE', req=True)
            +
            rg2hb_xsl('STRICT_MONITORING')
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
            +
            # deprecated ones
            rg2hb_xsl('NETSERVICENAME', req=Warning)
            +
            rg2hb_xsl('DBJ2EE_ONLY', req=Warning)
            +
            rg2hb_xsl('JAVA_HOME', req=Warning)
            +
            rg2hb_xsl('DIR_BOOTSTRAP', req=Warning)
            +
            rg2hb_xsl('DIR_SECSTORE', req=Warning)
            +
            rg2hb_xsl('DB_JARS', req=Warning)
) + '''
        </instance_attributes>
    </xsl:when>
'''
