# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec


ccsflat2pcs = '''\
    <!--
        LVM ~ lvm
     -->
    <xsl:when test="name() = 'lvm'">
''' + \
        ResourceSpec('ocf:heartbeat:LVM').xsl_attrs \
+ '''
        <!-- SHOW-STOPPERS -->
        <xsl:if test="@lv_name">
            <xsl:message terminate="true"
            >Cannot convert LV binding, stick with whole VG one</xsl:message>
        </xsl:if>

        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- volgrpname ~ vg_name -->
            <nvpair id="{concat($Prefix, '-ATTRS-volgrpname')}"
                    name="volgrpname"
                    value="{@vg_name}"/>
            <!-- exclusive: implied -->
            <nvpair id="{concat($Prefix, '-ATTRS-exclusive')}"
                    name="exclusive"
                    value="true"/>
        </instance_attributes>
    </xsl:when>
'''
