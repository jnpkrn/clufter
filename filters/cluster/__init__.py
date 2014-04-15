# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# yield corosync v.1/flatiron configuration compatible with el6.{5,...}
ccs2flatironxml = '''\
    <!-- cluster=current ~ corosync -->
    <corosync>

        <!-- just include Pacemaker plugin, rest is kept in cluster.conf -->
        <service name="pacemaker"
                 ver="1"/>

    </corosync>
'''

# yield corosync v.2/needle configuration compatible with el7
# diff to ccs2flatironxml (note that "corosync" is used as pseudoroot):
# - specify pseudoroot/totem/@cluster_name
# - enumerate cluster nodes via /pseudoroot/nodelist
# - do not use Pacemaker plugin via /pseudoroot/service[@name='pacemaker']
# - possibly specify /pseudoroot/quorum
ccs2needlexml = '''\
    <!-- cluster=current ~ corosync -->
    <corosync>

        <!-- clusternodes ~ nodelist -->
        <clufter:descent at="clusternodes"/>

        <!-- cman ~ quorum -->
        <clufter:descent at="cman"/>

        <!-- logging ~ logging -->
        <clufter:descent at="logging"/>

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
            <clufter:descent at="totem"/>
        </totem>

    </corosync>
'''

flatccs2pcs = '''\
    <cib validate-with="pacemaker-1.2"
         admin_epoch="1"
         epoch="1"
         num_updates="0"

         update-client="clufter">
        <configuration>
            <crm_config>
                <!-- cluster_property_set id="cib-bootstrap-options">
                  <nvpair id="startup-fencing" name="startup-fencing" value="true"/>

                  <- this is default, but should be set to false when no fence devices present ->
                  <nvpair id="stonith-enabled" name="stonith-enabled" value="true"/>

                  <- this is moved to crm_attribute -type rsc_defaults -attr-name is-managed -attr-value false ->
                  <nvpair id="default-resource-stickiness" name="default-resource-stickiness" value="INFINITY"/>
                </cluster_property_set -->
            </crm_config>
            <clufter:descent at="clusternodes"/>
            <resources>

                <!--
                    fencing/stonith configuration
                  -->

                <!-- device-wide parameters -> resource templates -->
                <clufter:descent at="fencedevice"/>

                <!-- per-node parameters -> resource primitives referencing
                     templates; above-zero score to restore semantic priority -->
                <xsl:for-each select="clusternodes/clusternode/fence/method/device">
                    <xsl:variable name="NodeName"
                                  select="../../../@name"/>
                    <xsl:variable name="Prefix"
                                  select="concat('FENCEINST-', @name, '-NODE-', $NodeName)"/>
                    <primitive id="{$Prefix}"
                               template="{concat('FENCEDEV-', @name)}">
                        <instance_attributes id="{concat($Prefix, '-ATTRS')}" score="1">
                        <xsl:for-each select="@*[name() != 'name' and name() != 'port']">
                            <nvpair id="{concat($Prefix, '-ATTRS-', name())}"
                                    name="{name()}"
                                    value="{.}"/>
                        </xsl:for-each>
                        <xsl:choose>
                        <xsl:when test="@port">
                            <nvpair id="{concat($Prefix, '-ATTRS-', 'pcmk_host_map')}"
                                    name="pcmk_host_map"
                                    value="{concat($NodeName, ':', @port)}"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <nvpair id="{concat($Prefix, '-ATTRS-', 'pcmk_host_list')}"
                                    name="pcmk_host_list"
                                    value="{$NodeName}"/>
                        </xsl:otherwise>
                        </xsl:choose>
                        </instance_attributes>
                    </primitive>
                </xsl:for-each>

                <!-- resources (TBD) -->

            </resources>
        </configuration>
        <status/>
    </cib>
'''

ccs2ccs_pcmk = '''\
    <clufter:descent-mix preserve-rest="true"/>

    <!-- CLUSTER config version bump -->
    <xsl:template match="cluster/@config_version">
        <xsl:attribute name="{name()}">
            <xsl:value-of select="string(. + 1)"/>
        </xsl:attribute>
    </xsl:template>
'''

# check http://stackoverflow.com/questions/4509662/how-to-generate-unique-string
# XXX device/@port for: fence_pcmk, fence_rhevm, fence_virsh, fence_{virt,xvm},
#                       fence_vmware{,_soap} (?)
# XXX cluster/@alias (not el6)
ccs_obfuscate_identifiers = '''\
    <clufter:descent-mix preserve-rest="true"/>

    <!-- CLUSTER-NAME -->

    <xsl:template match="cluster/@name">
        <xsl:attribute name="{name()}">
            <xsl:value-of select="'CLUSTER-NAME'"/>
        </xsl:attribute>
    </xsl:template>

    <!-- CLUSTER-NODE -->

    <!-- hostnames are treated in case-insensitive manner... -->
    <xsl:variable name="AlphaUpper"
                  select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
    <xsl:variable name="AlphaLower"
                  select="'abcdefghijklmnopqrstuvwxyz'"/>

    <xsl:variable name="ClusterNode"
                  select="cluster/clusternodes/clusternode[@name]"/>
    <xsl:template match="
        cluster/clusternodes/clusternode/@name
        |cluster/clusternodes/clusternode/fence/method/device/@nodename
        |cluster/clusternodes/clusternode/fence/method/device/@port
        |cluster/rm/failoverdomains/failoverdomain/failoverdomainnode/@name">
        <xsl:variable name="ClusterNodeMatch"
                      select="$ClusterNode[
                                  translate(@name, $AlphaUpper, $AlphaLower)
                                  =
                                  translate(current(), $AlphaUpper, $AlphaLower)
                              ][1]"/>
        <xsl:attribute name="{name()}">
            <xsl:choose>
                <xsl:when test="$ClusterNodeMatch">
                    <!-- 1+ match(es) found -->
                    <xsl:value-of select="concat(
                        'CLUSTER-NODE-',
                        count($ClusterNodeMatch/preceding-sibling::clusternode) + 1
                    )"/>
                </xsl:when>
                <xsl:when test="name() = 'port'">
                    <!-- conservative approach with @port -->
                    <xsl:value-of select="."/>
                </xsl:when>
                <xsl:otherwise>
                    <!-- probably refential integrity error -->
                    <xsl:value-of select="concat(
                        'CLUSTER-NODE-UNDEF-',
                        generate-id()
                    )"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:attribute>
    </xsl:template>

    <!-- FENCE-DEVICE -->

    <xsl:variable name="FenceDevice"
                  select="cluster/fencedevices/fencedevice[@name]"/>
    <xsl:template match="
        cluster/fencedevices/fencedevice/@name
        |cluster/clusternodes/clusternode/fence/method/device/@name">
        <xsl:variable name="FenceDeviceMatch"
                      select="$FenceDevice[
                                  @name
                                  =
                                  current()
                              ][1]"/>
        <xsl:attribute name="{name()}">
            <xsl:choose>
                <xsl:when test="$FenceDeviceMatch">
                    <!-- 1+ match(es) found -->
                    <xsl:value-of select="concat(
                        'FENCE-DEVICE-',
                        count($FenceDeviceMatch/preceding-sibling::fencedevice) + 1
                    )"/>
                </xsl:when>
                <xsl:otherwise>
                    <!-- probably refential integrity error -->
                    <xsl:value-of select="concat(
                        'FENCE-DEVICE-UNDEF-',
                        generate-id()
                    )"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:attribute>
    </xsl:template>
'''
