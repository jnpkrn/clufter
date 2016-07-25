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

ccsflat2cibprelude = ('''\
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
''' + (
            rg2hb_xsl('java_home', '/usr/lib/jvm/jre', req=abs)
            +
            rg2hb_xsl('catalina_home', '{$pcscmd_tomcat_catalina_home}',
                      req=abs)
) + '''\
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
        squote("NOTE: cannot convert tomcat-6 resource directly,"
               " prefilling defaults; "),
        squote("consider manual completion based on /etc/tomcat6/tomcat6.conf ("),
        "@config_file",
        squote(") file (or switching to LSB/systemd)")
    ))
)
