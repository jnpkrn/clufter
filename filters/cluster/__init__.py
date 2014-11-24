# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following 2nd chance import is to allow direct usage context (testing, etc.)
try:
    from ....utils_xslt import xslt_is_member
except ValueError:  # Value?
    from ...utils_xslt import xslt_is_member

###

from base64 import b64encode
from hashlib import sha256
from os import getpid
from time import time

# yield corosync v.2/needle configuration compatible with el7
ccs2needlexml = ('''\
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
''' + ( \
                        xslt_is_member('.', ('udp',
                                             'udpu'))
) + ''']">
                        <xsl:copy-of select="cman/@transport"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:message>
                            <xsl:value-of select="concat('Unsupported value for `transport',
                                                         &quot;'&quot;, ' dropped: ',
                                                         cman/@transport)"/>
                        </xsl:message>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:if>
            <clufter:descent at="totem">
                <!-- see bz1165821 (pcs currently doesn't handle corosync's keyfile) -->
                <xsl:if test="not(totem) or totem[
                                  (
                                      not(@secauth)
                                      or
                                      @secauth != 'off'
                                  )
                                  and
                                  not(@keyfile)
                              ]">
                    <xsl:message>%(key_message)s</xsl:message>
                    <xsl:attribute name="key">
                        <xsl:value-of select="'%(key)s'"/>
                    </xsl:attribute>
                </xsl:if>
            </clufter:descent>
            <!-- XXX bz1078343 -->
            <!-- xsl:if test="not(totem) or not(@token)">
                <xsl:attribute name="token">10000</xsl:attribute>
            </xsl:if -->
        </totem>

        <!-- uidgid ~ uidgid -->
        <clufter:descent at="uidgid"/>

    </corosync>
''') % dict(
    # NB: nothing against second parameter to b64encode, but it seems to be
    #     slower than simple chained replacement (a la urlsafe_b64encode)
    key='_NOT_SECRET--' + b64encode(sha256(
        str(getpid()) + '_REALLY_' + str(int(time()))
    ).digest()).replace('+', '-').replace('/', '_').rstrip('='),
    key_message='WARNING: secret key used by corosync for encryption/integrity'
                ' checking is, as a measure to prevent from dropping these'
                ' security features entirely, stored directly in the main'
                ' configuration file, possibly readable by arbitrary'
                ' system-local user',
)

###

try:
    from .... import package_name, version
except ValueError:
    from ... import package_name, version
ccsflat2pcsprelude_self_id = "{0} {1}".format(package_name(), version)

# should roughly match the output of:
# (exec 3>&1; exec >/dev/null; export CIB_shadow=test-shadow;
#  crm_shadow -bfe "${CIB_shadow}"; cat "$(crm_shadow -bF)">&3;
#  crm_shadow -bfD "${CIB_shadow}")
# <cib epoch="0" num_updates="0" admin_epoch="0" validate-with="pacemaker-1.2"
#      cib-last-written="Wed Oct 22 15:14:04 2014">
#   <configuration>
#     <crm_config/>
#     <nodes/>
#     <resources/>
#     <constraints/>
#   </configuration>
#   <status/>
# </cib>
ccsflat2pcsprelude = ('''\
    <cib validate-with="pacemaker-1.2"
         admin_epoch="0"
         epoch="0"
         num_updates="0"

         update-client="%(self_id)s">
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
                    FENCING/STONITH CONFIGURATION
                 -->

                <xsl:comment> FENCING/STONITH (+ POSSIBLY TOPOLOGY BELOW) </xsl:comment>

                <!-- device-wide (fencedev) parameters -> resource templates -->
                <clufter:descent at="fencedevice"/>

                <!-- per-node (fenceinst) parameters -> resource primitives
                                                        referencing templates;
                     above-zero score to restore semantic priority -->
                <xsl:for-each select="clusternodes/clusternode/fence/method/device">
                    <xsl:variable name="Node"
                                  select="../../.."/>
                    <xsl:variable name="NodeName"
                                  select="$Node/@name"/>
                    <xsl:choose>
                        <!-- prevent emitting duplicate (id) primitives -->
                        <xsl:when test="generate-id(
                                            $Node/fence/method/device[
                                                @name = current()/@name
                                                and
                                                (
                                                    not(@port)
                                                    or
                                                    @port = current()/@port
                                                )
                                            ]
                                        ) = generate-id()">
                            <xsl:variable name="Prefix">
                                <xsl:value-of select="concat('FENCEINST-', @name, '-NODE-', $NodeName)"/>
                                <xsl:if test="@port">
                                    <xsl:value-of select="concat('-', @port)"/>
                                </xsl:if>
                            </xsl:variable>
                            <primitive id="{$Prefix}"
                                       template="{concat('FENCEDEV-', @name)}">
                                <instance_attributes id="{concat($Prefix, '-ATTRS')}" score="1">
                                <xsl:for-each select="@*[name() != 'name' and name() != 'port']">
                                    <nvpair id="{concat($Prefix, '-ATTRS-', name())}"
                                            name="{name()}"
                                            value="{.}"/>
                                </xsl:for-each>
                                <xsl:choose>
                                <!-- both below lead to pcmk_host_check = static-list,
                                     nothing more needed -->
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
                        </xsl:when>
                    </xsl:choose>
                </xsl:for-each>


                <!--
                    RESOURCES+ARRANGEMENT CONFIGURATION
                 -->

                <xsl:comment> RESOURCES+ARRANGEMENT </xsl:comment>

                <clufter:descent at="rm"/>

            </resources>
            <constraints>
                <!-- TODO, just to prevent validation failure -->
            </constraints>

            <!--
                FENCING TOPOLOGY
             -->

            <fencing-topology>
            <xsl:for-each select="clusternodes/clusternode[
                                      count(fence/method) &gt; 1
                                      or
                                      fence/method[
                                          count(device) &gt; 1
                                      ]
                                  ]">
                    <xsl:variable name="NodeName"
                                  select="./@name"/>
                    <xsl:for-each select="fence/method">
                        <xsl:variable name="Method"
                                      select="."/>
                        <xsl:variable name="Index"
                                      select="string(position())"/>
                        <fencing-level id="{concat('FENCING-', $NodeName, '-', $Index, '-', @name)}"
                                       target="{concat('NODE-', $NodeName)}"
                                       index="{$Index}">
                            <xsl:attribute name="devices">
                                <xsl:for-each select="device">
                                    <xsl:if test="position() != 1">
                                        <xsl:value-of select="','"/>
                                    </xsl:if>
                                    <xsl:value-of select="@name"/>
                                </xsl:for-each>
                            </xsl:attribute>
                        </fencing-level>
                    </xsl:for-each>
            </xsl:for-each>
            </fencing-topology>

        </configuration>
        <status/>
    </cib>
''') % dict(self_id=ccsflat2pcsprelude_self_id)

###

ccs_revitalize = '''\
    <clufter:descent-mix preserve-rest="true"/>

    <!--
        FENCING/STONITH CONFIGURATION
        see also: fencedevices/fencedevice
     -->

    <xsl:template match="cluster/clusternodes/clusternode/fence/method/device
                         |cluster/clusternodes/clusternode/unfence/device">
        <xsl:variable name="FenceInst" select="."/>
        <xsl:copy>
            <xsl:for-each select="@*">
                <xsl:choose>
                    <!-- virt/xvm: domain -> port -->
                    <xsl:when test="name() = 'domain'
                                    and
                                    /cluster/fencedevices/fencedevice[
                                        @name = $FenceInst/@name
                                        and
                                        (
                                            @agent = 'fence_virt'
                                            or
                                            @agent = 'fence_xvm'
                                        )
                                    ]">
                        <xsl:attribute name='port'>
                            <xsl:value-of select="."/>
                        </xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:copy/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
            <xsl:apply-templates select="*"/>
        </xsl:copy>
    </xsl:template>
'''

###

ccs2ccs_pcmk = '''\
    <clufter:descent-mix preserve-rest="true"/>

    <!-- CLUSTER config version bump -->
    <xsl:template match="cluster/@config_version">
        <xsl:attribute name="{name()}">
            <xsl:value-of select="string(. + 1)"/>
        </xsl:attribute>
    </xsl:template>
'''

###

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
