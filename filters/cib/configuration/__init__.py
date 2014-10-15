# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


pcsprelude2pcscompact = '''\
    <clufter:descent-mix preserve-rest="true"/>
    <!-- strip empty optional elements -->
    <xsl:template match="fencing-topology[count(*) = 0]"/>
'''

###

pcscompact2pcs = ('''\
    <xsl:template match="crm_config[
                             not(
                                 following-sibling::resources/primitive[
                                     @class = 'stonith'
                                 ]|following-sibling::resources/primitive[
                                     preceding-sibling::template[
                                         @class = 'stonith'
                                         and
                                         @id = current()/@template
                                     ]
                                 ]
                             )
                         ]">
        <xsl:copy>
        <xsl:comment> %(note_stonith)s </xsl:comment>
        <xsl:message>%(note_stonith)s</xsl:message>
        <cluster_property_set id="CRMCONFIG-bootstrap">
            <nvpair id="CRMCONFIG-bootstrap-STONITH-ENABLED"
                    name="stonith-enabled"
                    value="false"/>
        </cluster_property_set>
        </xsl:copy>
    </xsl:template>
''') % dict(
    note_stonith="NOTE: no fencing is configured hence stonith is disabled;"
                 " please note, however, that this is suboptimal, especially"
                 " in shared storage scenarios"
)
