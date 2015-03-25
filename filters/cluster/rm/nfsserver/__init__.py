# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec, rg2hb_xsl


ccsflat2cibprelude = '''\
    <!--
        nfsserver ~ nfsserver
     -->
    <xsl:when test="name() = 'nfsserver'">
''' + (
        ResourceSpec('ocf:heartbeat:nfsserver').xsl_attrs
) + '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
''' + (
            rg2hb_xsl('nfs_shared_infodir', 'nfspath')
            +
            # see rhbz#918315 + rhbz#1096376/7
            rg2hb_xsl('statd_port', 'statdport')
) + '''\
        </instance_attributes>
    </xsl:when>
'''

###

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@path',
                     kind='I', own=True, desc='exported path'),
))
