# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl


ccsflat2cibprelude = '''\
    <!--
        LVM ~ lvm
     -->
    <xsl:when test="name() = 'lvm'">
''' + (
        ResourceSpec('ocf:heartbeat:LVM').xsl_attrs
) + '''
        <!-- SHOW-STOPPERS -->
        <xsl:if test="@lv_name">
            <xsl:message terminate="true"
            >Cannot convert LV binding, stick with whole VG one [https://bugzilla.redhat.com/1286292]</xsl:message>
        </xsl:if>

        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
''' + (
            rg2hb_xsl('volgrpname', 'vg_name', req=True)
            +
            rg2hb_xsl('exclusive', 'true', req=abs)
) + '''\
        </instance_attributes>
    </xsl:when>
'''
