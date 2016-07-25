# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl

ccsflat2cibprelude = ('''\
    <!--
        native initscript/systemd unitfile ~ samba
     -->
    <xsl:when test="name() = 'samba'">
        <xsl:choose>
            <xsl:when test="$pcscmd_init_sys = 'systemd'">
''' + (
                ResourceSpec('systemd:smb').xsl_attrs
) + '''\
            </xsl:when>
            <xsl:when test="$pcscmd_init_sys = 'sysvinit'">
''' + (
                ResourceSpec('lsb:smb').xsl_attrs
) + '''\
            </xsl:when>
            <xsl:when test="$pcscmd_init_sys = 'upstart'">
                <!-- XXX could be either lsb, service or upstart
                         (as far as RHEL 6 is concerned),
                         service seems to be most canonical, though -->
''' + (
                ResourceSpec('service:smb').xsl_attrs
) + '''\
            </xsl:when>
            <xsl:otherwise>
''' + (
                ResourceSpec('service:smb').xsl_attrs
) + '''\
                <xsl:comment> %(msg_provider_guess)s </xsl:comment>
                <xsl:message>%(msg_provider_guess)s</xsl:message>
            </xsl:otherwise>
        </xsl:choose>

        <xsl:if test="@config_file or @smbd_options or @nmbd_options">
            <xsl:comment> %(msg_ignored_params)s </xsl:comment>
            <xsl:message>%(msg_ignored_params)s</xsl:message>
        </xsl:if>

        <!-- OPERATIONS -->
        <operations>
''' + (
            rg2hb_xsl('stop', 'shutdown_wait', op=True)
) + '''\
        </operations>
    </xsl:when>
''') % dict(
    msg_provider_guess="WARNING: knowledge of how to start samba on the target"
                       " system missing, assuming `service' provider",
    msg_ignored_params="NOTE: cannot convert samba resource directly, hence"
                       " some configuration bits can be lost"
                       " (config_file,smbd_options, nmbd_options)",
)

###

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@config_file',
                     kind='A', desc='configuration file'),
))
