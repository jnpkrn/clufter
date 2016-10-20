# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl


ccsflat2cibprelude = '''\
    <!--
        LVM ~ lvm
     -->

    <!-- SHOW-STOPPERS -->

    <xsl:when test="name() = 'lvm'
                    and
                    @lv_name
                    and
                    count(
                        (following-sibling::lvm
                        |../following-sibling::service/lvm)[
                            @vg_name = current()/@vg_name
                            and
                            @lv_name != current()/@lv_name
                        ]
                    ) = 1">
        <xsl:message terminate="true">
            <xsl:value-of select="concat('Cannot convert lvm when there are',
                                         ' multiple LV bindings for single',
                                         '`', @vg_name, '` VG')"/>
        </xsl:message>
    </xsl:when>

    <!-- STANDARD MODE OF OPERATION -->

    <xsl:when test="name() = 'lvm'">
''' + (
        ResourceSpec('ocf:heartbeat:LVM').xsl_attrs
) + '''
        <xsl:if test="@lv_name">
            <xsl:message>
                <xsl:value-of select="concat('NOTE: LV binding `', @lv_name,
                                             '` unused, it is assumed you have',
                                             ' just a single LV at `', @vg_name,
                                             '` VG')"/>
            </xsl:message>
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
