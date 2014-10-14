# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_cib import ResourceSpec


ccsflat2pcsprelude = '''\
    <!--
        nfsserver ~ nfserver
     -->
    <xsl:when test="name() = 'nfsserver'">
''' + \
        ResourceSpec('ocf:heartbeat:nfsserver').xsl_attrs \
+ '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- nfs_shared_infodir ~ nfspath -->
            <xsl:if test="@nfsserver">
            <nvpair id="{concat($Prefix, '-ATTRS-nfs_shared_infodir')}"
                    name="nfs_shared_infodir"
                    value="{@nfsserver}"/>
            </xsl:if>
        </instance_attributes>
    </xsl:when>
'''

###

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@path',
                     kind='I', own=True, desc='exported path'),
))
