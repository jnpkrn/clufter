# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....utils_xml import squote

ccsflat2cibprelude = ('''\
    <!--
        lsb:<script> ~ script;  starts-with(@file, '/etc/init.d/')
     -->
    <xsl:when test="name() = 'script'
                    and
                    starts-with(@file, '/etc/init.d/')">
        <xsl:attribute name="class">lsb</xsl:attribute>
        <xsl:attribute name="type">
            <xsl:value-of select="substring-after(@file, '/etc/init.d/')"/>
        </xsl:attribute>
    </xsl:when>

    <!--
        lsb:<script> ~ script; not(starts-with(@file, '/etc/init.d/')) -> hack
     -->
    <xsl:when test="name() = 'script'
                    and
                    not(starts-with(@file, '/etc/init.d/'))">
        <xsl:attribute name="class">lsb</xsl:attribute>
        <xsl:attribute name="type">
            <xsl:value-of select="concat('../../../', @file)"/>
        </xsl:attribute>
        <xsl:comment><xsl:value-of select="concat(' ', %(note)s, ' ')"/></xsl:comment>
        <xsl:message><xsl:value-of select="concat(%(note)s)"/></xsl:message>
    </xsl:when>
''') % dict(
    note=', '.join((
        squote("NOTE: consider moving `"),
        "@file",
        squote("` into canonical LSB scripts location (standard: `/etc/init.d/`)"
               " + reflecting this in the configuration, perhaps even"
               " switching to an equivalent (systemd, anything OCF RA, ...)")
    ))
)

###

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@file',
                     kind='X', desc='LSB compliant initscript'),
))
