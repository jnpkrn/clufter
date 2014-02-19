# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

ccs2coroxml = '''\
    <!-- cluster=current ~ corosync -->
    <corosync>

        <!-- clusternodes ~ nodelist</xsl:comment -->
        <clufter:recursion at="clusternodes"/>

        <!-- cman ~ quorum -->
        <clufter:recursion at="cman"/>

        <!-- logging ~ logging -->
        <clufter:recursion at="logging"/>

        <!-- totem (pieces from cluster=current and cman) ~ totem -->
        <totem version="2"
               cluster_name="{@name}">
            <xsl:if test="cman/@transport">
                <xsl:choose>
                    <xsl:when test="cman/@transport[
                        contains(concat(
                            '|udp',
                            '|udpu',
                            '|'), concat('|', ., '|'))]">
                        <xsl:copy-of select="cman/@transport"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:message>
                            <xsl:value-of select="concat('Unsupported value for `transport&quot; dropped: ', .)"/>
                        </xsl:message>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:if>
            <clufter:recursion at="totem"/>
        </totem>
    </corosync>
'''

ccsflat2pcs = '''\
    <cib validate-with="pacemaker-1.1" admin_epoch="1" epoch="1" num_updates="0" have-quorum="1">
        <configuration>
            <crm_config>
                <!-- cluster_property_set id="cib-bootstrap-options">
                  <nvpair id="startup-fencing" name="startup-fencing" value="true"/>
                  <nvpair id="stonith-enabled" name="stonith-enabled" value="true"/>
                  <nvpair id="default-resource-stickiness" name="default-resource-stickiness" value="INFINITY"/>
                </cluster_property_set -->
            </crm_config>
            <clufter:recursion at="clusternodes"/>
            <clufter:recursion at="rm"/>
        </configuration>
        <status/>
    </cib>
'''

obfuscate_credentials = '''\
    <xsl:template match="*">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <clufter:recursion/>
       </xsl:copy>
    </xsl:template>
'''

# check http://stackoverflow.com/questions/4509662/how-to-generate-unique-string
# todo: comments on top-level not supported
obfuscate_identifiers = '''\
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
            <!--clufter:recursion/-->
       </xsl:copy>
    </xsl:template>

    <xsl:template match="cluster/@name">
        <xsl:attribute name="{name()}">
            <xsl:value-of select="'CLUSTER'"/>
        </xsl:attribute>
    </xsl:template>

    <xsl:variable name="ClusterNode" select="cluster/clusternodes/clusternode[@name]"/>
    <xsl:template match="cluster/clusternodes/clusternode/@name
                        |cluster/clusternodes/clusternode/fence/method/device/@nodename
                        |cluster/rm/failoverdomains/failoverdomain/failoverdomainnode/@name">
        <xsl:variable name="attr_name" select="."/>
        <xsl:attribute name="{name()}">
            <xsl:value-of select="concat('CLUSTER-NODE-UNDEF-', generate-id(.))"/>
        </xsl:attribute>
        <xsl:attribute name="{name()}">
            <xsl:for-each select="$ClusterNode">
                <xsl:if test="@name = $attr_name">
                    <xsl:value-of select="concat('CLUSTER-NODE-', position())"/>
                </xsl:if>
            </xsl:for-each>
        </xsl:attribute>
        <xsl:apply-templates select="@*|node()"/>
    </xsl:template>

    <xsl:variable name="FenceDevice" select="cluster/fencedevices/fencedevice[@name]"/>
    <xsl:template match="cluster/fencedevices/fencedevice/@name
                        |cluster/clusternodes/clusternode/fence/method/device/@name">
        <xsl:variable name="attr_name" select="."/>
        <xsl:attribute name="{name()}">
            <xsl:value-of select="concat('FENCE-DEVICE-UNDEF-', generate-id(.))"/>
        </xsl:attribute>
        <xsl:attribute name="{name()}">
            <xsl:for-each select="$FenceDevice">
                <xsl:if test="@name = $attr_name">
                    <xsl:value-of select="concat('FENCE-DEVICE-', position())"/>
                </xsl:if>
            </xsl:for-each>
        </xsl:attribute>
        <xsl:apply-templates select="@*|node()"/>
    </xsl:template>
'''
