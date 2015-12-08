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
        exportfs ~ nfsclient
     -->
    <xsl:when test="name() = 'nfsclient'">
''' + (
        ResourceSpec('ocf:heartbeat:exportfs').xsl_attrs
) + '''

        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
''' + (
            rg2hb_xsl('clientspec', 'target', req=True)
            +
            rg2hb_xsl('directory', 'path', req=True)
            +
            rg2hb_xsl('options')
) + '''\
            <xsl:comment><xsl:value-of select="concat(' ', %(note)s, ' ')"/></xsl:comment>
            <xsl:message><xsl:value-of select="concat(%(note)s)"/></xsl:message>
''' + (
            rg2hb_xsl('unlock_on_stop', 'false', req=abs)
) + '''\
        </instance_attributes>
    </xsl:when>
''') % dict(
    note=', '.join((
        squote("NOTE: explicitly disabling `unlock_on_stop` parameter for"),
        squote(" `exportfs` resource so as to preserve original `nfsclient`"),
        squote(" resource behavior; you may want to enable it, though"),
    ))
)
