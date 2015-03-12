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
from ....utils_xml import squote

ccsflat2pcsprelude = ('''\
    <!--
        tomcat ~ tomcat-6
     -->
    <xsl:when test="name() = 'tomcat-6'">
''' + (
        ResourceSpec('ocf:heartbeat:tomcat').xsl_attrs
) + '''
        <xsl:comment><xsl:value-of select="concat(' ', %(note)s, ' ')"/></xsl:comment>
        <xsl:message><xsl:value-of select="concat(%(note)s)"/></xsl:message>

        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <xsl:choose>
                <!-- NOTE we rely on atmost single dot separator
                     in the version, hence conformity with IEEE 754 -->
                <xsl:when test="$system = 'linux' and (
                    $system_1 = 'fedora' and $system_2 &gt;= 20
                    )">
''' + (
                    rg2hb_xsl('java_home', '/usr/lib/jvm/jre-1.8.0', req=abs)
                    +
                    rg2hb_xsl('catalina_home', '/usr/share/tomcat', req=abs)
) + '''\
                </xsl:when>
                <xsl:when test="$system = 'linux' and (
                    $system_1 = 'redhat' and $system_2 &gt;= 7
                    or
                    $system_1 = 'fedora' and $system_2 &gt;= 17
                    )">
''' + (
                    rg2hb_xsl('java_home', '/usr/lib/jvm/jre-1.7.0', req=abs)
                    +
                    rg2hb_xsl('catalina_home', '/usr/share/tomcat', req=abs)
) + '''\
                </xsl:when>
                <xsl:otherwise>
''' + (
                    # especially RHEL 6
                    rg2hb_xsl('java_home', '/usr/lib/jvm/jre-1.5.0', req=abs)
                    +
                    rg2hb_xsl('catalina_home', '/usr/share/tomcat6', req=abs)
) + '''\
                </xsl:otherwise>
        </instance_attributes>

        <!-- OPERATIONS -->
        <operations>
''' + (
            rg2hb_xsl('stop', 'shutdown_wait', op=True)
) + '''\
        </operations>
    </xsl:when>
''') % dict(
    note=', '.join((
        squote("NOTE: cannot convert directly, prefilling defaults; "),
        squote("consider manual completion based on /etc/tomcat6/tomcat6.conf ("),
        "@config_file",
        squote(") file (or switching to LSB/systemd)")
    ))
)
