# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following 2nd chance import is to allow direct usage context (testing, etc.)
try:
    from ....utils_xslt import xslt_is_member
except ValueError:  # Value?
    from ...utils_xslt import xslt_is_member

###

ccs_propagate_cman = '''\
    <xsl:template match="cman/@*[not(
''' + (
                        xslt_is_member('.', ('cman',
                                             'expected_votes'))
) + ''')] | cman/altmulticast
          | cman/multicast"/>

    <xsl:template match="cluster">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <totem>
                <!-- general variables -->
                <xsl:variable name="SpecBroadcast"
                              select="cman/@broadcast = 'yes'
                                      or
                                      cman/@transport = 'udpb'"/>
                <xsl:variable name="SpecToken">
                    <xsl:choose>
                        <xsl:when test="not(totem/@token)">
                            <xsl:value-of select="10000"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="totem/@token"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <!-- primary ring variables -->
                <xsl:variable name="SpecPrimaryAddr"
                              select="cman/multicast/@addr"/>
                <xsl:variable name="SpecPrimaryPort"
                              select="cman/@port
                                    |cman/multicast/@port"/>
                <xsl:variable name="SpecPrimaryTTL"
                              select="cman/multicast/@ttl"/>
                <xsl:variable name="SpecPrimaryEmit"
                              select="$SpecBroadcast
                                      or
                                      $SpecPrimaryAddr
                                      or
                                      $SpecPrimaryPort
                                      or
                                      $SpecPrimaryTTL != 1"/>
                <!-- secondary ring variables -->
                <xsl:variable name="SpecFirstNodeAltnames"
                              select="count(
                                          clusternodes/clusternode[1]/altname
                                      )"/>
                <xsl:variable name="SpecAltnamesSameCount"
                              select="count(
                                          clusternodes/clusternode
                                      )
                                      =
                                      count(
                                          clusternodes/clusternode[
                                              count(altname)
                                              =
                                              count(following-sibling::clusternode/altname)
                                          ]
                                      ) + 1
                                      "/>
                <xsl:variable name="SpecAltnamesSameNonzeroCount"
                              select="$SpecAltnamesSameCount
                                      and
                                      clusternodes/clusternode/altname"/>
                <xsl:variable name="SpecSecondaryAddr"
                              select="cman/altmulticast/@addr"/>
                <xsl:variable name="SpecSecondaryPort"
                              select="cman/@port
                                      |cman/altmulticast/@port"/>
                <xsl:variable name="SpecSecondaryTTL"
                              select="cman/altmulticast/@ttl"/>
                <xsl:variable name="SpecSecondaryEmit"
                              select="$SpecAltnamesSameNonzeroCount
                                      and
                                      (
                                          $SpecSecondaryAddr
                                          or
                                          $SpecSecondaryPort
                                          or
                                          $SpecSecondaryTTL != 1
                                      )"/>
                <!--
                    totem attributes
                 -->
                <xsl:copy-of select="totem/@*[
                    not(
                        name() = 'join' and number(.) = 50
                        or
                        name() = 'token' and number(.) = 1000
                    )]"/>
                <!-- see also bz214290 (corosync default: 50) -->
                <xsl:if test="not(totem/@join)">
                    <xsl:attribute name="join">60</xsl:attribute>
                </xsl:if>
                <!-- see also bz1078343 (corosync default: 1000) -->
                <xsl:attribute name="token">
                    <xsl:value-of select="$SpecToken"/>
                </xsl:attribute>
                <xsl:if test="$SpecSecondaryEmit
                              or
                              count(totem/interface) &gt; 1">
                    <xsl:attribute name="rrp_mode">passive</xsl:attribute>
                    <xsl:attribute name="rrp_problem_count_threshold">3</xsl:attribute>
                </xsl:if>
                <xsl:if test="not(totem/@consensus)">
                    <xsl:attribute name="consensus">
                        <xsl:choose>
                            <xsl:when test="count(clusternodes/clusternode) &gt; 2">
                                <xsl:variable name="SpecConsensus"
                                              select="$SpecToken * 0.2"/>
                                <xsl:choose>
                                    <xsl:when test="$SpecConsensus &lt; 200">
                                        <xsl:value-of select="200"/>
                                    </xsl:when>
                                    <xsl:when test="$SpecConsensus &gt; 2000">
                                        <xsl:value-of select="2000"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="$SpecConsensus"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$SpecToken + 2000"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                </xsl:if>
                <xsl:if test="cman/@transport">
                    <xsl:choose>
                        <xsl:when test="cman/@transport = 'udpu'">
                            <xsl:copy-of select="cman/@transport"/>
                        </xsl:when>
                        <xsl:when test="cman/@transport = 'rdma'">
                            <xsl:attribute name="transport">iba</xsl:attribute>
                        </xsl:when>
                        <xsl:when test="cman/@transport[
    ''' + (
                            xslt_is_member('.', ('udpb',
                                                 'udpu'))
    ) + ''']">
                            <!-- just drop it -->
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
                <xsl:apply-templates select="totem/interface[
                        @ringnumber &lt;
                            1 + count(/cluster/clusternodes/clusternode/altname)
                    ]"/>
                <!-- primary ring -->
                <xsl:if test="$SpecPrimaryEmit">
                    <interface ringnumber="0">
                        <xsl:if test="$SpecBroadcast">
                            <xsl:attribute name="broadcast">yes</xsl:attribute>
                        </xsl:if>
                        <xsl:if test="$SpecPrimaryAddr">
                            <xsl:attribute name="mcastaddr">
                                <xsl:value-of select="$SpecPrimaryAddr"/>
                            </xsl:attribute>
                        </xsl:if>
                        <xsl:if test="$SpecPrimaryPort">
                            <xsl:attribute name="mcastport">
                                <xsl:value-of select="$SpecPrimaryPort"/>
                            </xsl:attribute>
                        </xsl:if>
                        <xsl:if test="$SpecPrimaryTTL != 0">
                            <xsl:attribute name="ttl">
                                <xsl:value-of select="$SpecPrimaryTTL"/>
                            </xsl:attribute>
                        </xsl:if>
                    </interface>
                </xsl:if>
                <!-- secondary ring -->
                <xsl:if test="$SpecSecondaryEmit">
                    <interface ringnumber="1">
                        <xsl:if test="$SpecBroadcast">
                            <xsl:attribute name="broadcast">yes</xsl:attribute>
                        </xsl:if>
                        <xsl:if test="$SpecSecondaryAddr">
                            <xsl:attribute name="mcastaddr">
                                <xsl:value-of select="$SpecSecondaryAddr"/>
                            </xsl:attribute>
                        </xsl:if>
                        <xsl:if test="$SpecSecondaryPort">
                            <xsl:attribute name="mcastport">
                                <xsl:value-of select="$SpecSecondaryPort"/>
                            </xsl:attribute>
                        </xsl:if>
                        <xsl:if test="$SpecSecondaryTTL != 0">
                            <xsl:attribute name="ttl">
                                <xsl:value-of select="$SpecSecondaryTTL"/>
                            </xsl:attribute>
                        </xsl:if>
                    </interface>
                </xsl:if>
            </totem>
            <xsl:apply-templates select="*[name() != 'totem']"/>
        </xsl:copy>
    </xsl:template>
'''

###

from base64 import b64encode
from hashlib import sha256
from os import getpid
from time import time

# following 2nd chance import is to allow direct usage context (testing, etc.)
try:
    from ....utils import lazystring
    from ....utils_prog import getenv_namespaced
except ValueError:  # Value?
    from ...utils import lazystring
    from ...utils_prog import getenv_namespaced


# yield corosync v.2/needle configuration compatible with el7
ccs2needlexml = lazystring(lambda: ('''\
    <!-- cluster=current ~ corosync -->
    <corosync>

        <!-- clusternodes ~ nodelist -->
        <clufter:descent at="clusternodes"/>

        <!-- cman ~ quorum -->
        <!--
            @provider to prevent crmd error:
            cluster_connect_quorum: Corosync quorum is not configured
        -->
        <quorum provider="corosync_votequorum">
            <clufter:descent at="cman"/>
            <!-- xsl:if test="cman/@expected_votes
                          and
                          quorumd/@votes">
                <! un-propagate quorumd votes from overall expected votes >
                <xsl:attribute name="expected_votes">
                    <xsl:value-of select="cman/@expected_votes
                                          -
                                          quorumd/@votes"/>
                </xsl:attribute>
            </xsl:if -->
        </quorum>

        <!-- logging ~ logging -->
        <clufter:descent at="logging"/>

        <!-- totem (pieces from cluster=current and cman) ~ totem -->
        <totem version="2"
               cluster_name="{@name}">
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
                    <xsl:attribute name="key"
                    >%(key)s</xsl:attribute>
                </xsl:if>
            </clufter:descent>
        </totem>

        <!-- uidgid ~ uidgid -->
        <clufter:descent at="uidgid"/>

    </corosync>
''') % dict(
    # NB: nothing against second parameter to b64encode, but it seems to be
    #     slower than simple chained replacement (a la urlsafe_b64encode)
    key='_NOT_SECRET' + (
        '--' + b64encode(sha256(
            str(getpid()) + '_REALLY_' + str(int(time()))
        ).digest()).replace('+', '-').replace('/', '_').rstrip('=')
        if getenv_namespaced('NOSALT', '0') in ('0', 'false') else '_'
    ),
    key_message='WARNING: secret key used by corosync for encryption/integrity'
                ' checking is, as a measure to prevent from dropping these'
                ' security features entirely, stored directly in the main'
                ' configuration file (totem/key), possibly readable by'
                ' arbitrary system-local user',
), cache=False)

###

try:
    from .... import package_name, version
    from ....utils_xslt import xslt_id_friendly
except ValueError:
    from ... import package_name, version
    from ...utils_xslt import xslt_id_friendly
ccsflat2cibprelude_self_id = "{0} {1}".format(package_name(), version)

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
ccsflat2cibprelude = ('''\
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
                                    <xsl:value-of select="concat(
                                        '-',
''' + (
                                        xslt_id_friendly('@port')
) + '''
                                    )"/>
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
                                      count(fence/method[device]) &gt; 1
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
''') % dict(self_id=ccsflat2cibprelude_self_id)

###

# following 2nd chance import is to allow direct usage context (testing, etc.)
try:
    from ....utils_xslt import xslt_is_member
except ValueError:  # Value?
    from ...utils_xslt import xslt_is_member

ccs_revitalize_fa_domain = tuple(
    'fence_' + agent for agent in ('virt', 'xvm')
)

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
''' + (
                                        xslt_is_member('@agent',
                                                       ccs_revitalize_fa_domain)
) + '''
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

ccs_version_bump = '''\
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
ccs_obfuscate_identifiers = '''\
    <clufter:descent-mix preserve-rest="true"/>

    <!-- CLUSTER-NAME -->

    <xsl:template match="cluster/@name">
        <xsl:attribute name="{name()}">
            <xsl:value-of select="'CLUSTER-NAME'"/>
        </xsl:attribute>
    </xsl:template>

    <!-- XXX: CLUSTER-ALIAS (not in el6 schemas) -->

    <xsl:template match="cluster/@alias">
        <xsl:attribute name="{name()}">
            <xsl:value-of select="'CLUSTER-ALIAS'"/>
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
        |cluster/clusternodes/clusternode/altname/@name
        |cluster/rm/failoverdomains/failoverdomain/failoverdomainnode/@name
        |cluster/clusternodes/clusternode//device/@*[name() != 'name']">
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
                        1 + count(
                            $ClusterNodeMatch/preceding-sibling::*[
                                count(.|$ClusterNode) = count($ClusterNode)
                            ]
                        )
                    )"/>
                </xsl:when>
                <xsl:when test="name() != 'name'">
                    <!-- rest of non-name ~ (un)fence device attributes -->
                    <xsl:value-of select="."/>
                </xsl:when>
                <xsl:when test="name(..) = 'altname'">
                    <!-- altname case, further customized prefix -->
                    <xsl:value-of select="concat(
                        'CLUSTER-NODE-ALT-',
                        1 + count(
                            ../../preceding-sibling::*[
                                count(.|$ClusterNode) = count($ClusterNode)
                            ]
                        )
                    )"/>
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
        |cluster/clusternodes/clusternode/fence/method/device/@name
        |cluster/clusternodes/clusternode/unfence/device/@name">
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

###

# following 2nd chance import is to allow direct usage context (testing, etc.)
try:
    from ....filters._2pcscmd import coro2pcscmd
except ValueError:  # Value?
    from ...filters._2pcscmd import coro2pcscmd

ccspcmk2pcscmd = coro2pcscmd(cman='', node='clusternode', totem='')
