# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec

ccsflat2cibprelude = '''\
    <!--
        native initscript/systemd unitfile ~ samba
     -->
    <xsl:when test="name() = 'samba'">
            <xsl:choose>
                <!-- NOTE we rely on atmost single dot separator
                     in the version, hence conformity with IEEE 754 -->
                <xsl:when test="$system = 'linux' and (
                    $system_1 = 'redhat' and $system_2 &gt;= 7
                    or
                    $system_1 = 'fedora' and $system_2 &gt;= 15
                    )">
''' + (
                    ResourceSpec('systemd:smb').xsl_attrs
) + '''
                </xsl:when>
                <xsl:when test="$system = 'linux' and (
                    $system_1 = 'redhat' and $system_2 &lt; 7
                    or
                    $system_1 = 'fedora' and $system_2 &lt; 15
                    ">
                    <!-- XXX could be either lsb, service or upstart
                             (as far as RHEL 6 is concerned),
                             service seems to be most canonical, though -->
''' + (
                    ResourceSpec('service:smb').xsl_attrs
) + '''
                </xsl:when>
                <xsl:otherwise>
                    <xsl:message terminate="true"
                    >Knowledge of how to start samba on your system missing</xsl:message>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:attribute>
    </xsl:when>
'''

###

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@config_file',
                     kind='A', desc='configuration file'),
))
