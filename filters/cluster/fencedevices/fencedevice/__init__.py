# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

ccsflat2cibprelude = '''\
    <template id="{concat('FENCEDEV-', @name)}"
              class="stonith"
              type="{@agent}">
        <xsl:variable name='FenceDevName' select="@name"/>
        <instance_attributes id="{concat('FENCEDEV-', @name, '-ATTRS')}">
        <xsl:for-each select="@*[name() != 'agent' and name() != 'name']">
            <nvpair id="{concat('FENCEDEV-', $FenceDevName, '-ATTRS-', name())}"
                    name="{name()}"
                    value="{.}"/>
        </xsl:for-each>
        </instance_attributes>
    </template>
'''

###

ccs_obfuscate_credentials_password = (
    'passwd',
    'snmp_priv_passwd',
)

ccs_obfuscate_credentials_login = (
    'login',
)

ccs_obfuscate_credentials = '''\
    <xsl:copy>
        <xsl:apply-templates select="@*"/>
        <xsl:for-each select="@*[
''' + (
        xslt_is_member('name()', ccs_obfuscate_credentials_password)
) + ''']">
            <xsl:attribute name="{name()}">SECRET-PASSWORD</xsl:attribute>
        </xsl:for-each>
        <xsl:for-each select="@*[
''' + (
        xslt_is_member('name()', ccs_obfuscate_credentials_login)
) + ''']">
            <xsl:attribute name="{name()}">SECRET-LOGIN</xsl:attribute>
        </xsl:for-each>
        <xsl:apply-templates/>
    </xsl:copy>
'''

###

ccs_revitalize = '''\
    <!-- xvm: domain -> port -->
    <xsl:template match="fencedevice[@agent = 'fence_xvm']">
        <xsl:copy>
            <xsl:for-each select="@*">
                <xsl:choose>
                    <xsl:when test="name() = 'domain'">
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

from ....filters.ccs_artefacts import artefact, artefact_cond

ccs_artefacts_common_params = (
    # #el6        # el7
    # alom        alom
    # apc         apc
    # bladecenter bladecenter
    #             brocade
    # drac5       drac5
    #             hds_cb
    # hpblade     hpblade
    # ilo_mp      ilo_mp
    # ldom        ldom
    # lpar        lpar
    # rsa         rsa
    # rsb         rsb
    # virsh       virsh
    # vmware      vmware
    # wti         wti
    artefact_cond('@identity_file', kind='S',
                  desc='FA: SSH identity file (private key)')
    ) + (
    # #el6         #el7
    # alom         alom
    # apc          apc
    # apc_snmp     apc_snmp
    # baytech      baytech
    # bladecenter  bladecenter
    # brocade      brocade
    # bullpap      bullpap
    # cisco_mds    cisco_mds
    # cisco_ucs    cisco_ucs
    # drac         drac
    # drac5        drac5
    # eaton_snmp   eaton_snmp
    # eps          eps
    #              hds_cb
    # hpblade      hpblade
    # ibmblade     ibmblade
    # ifmib        ifmib
    # ilo          ilo
    # ilo_mp       ilo_mp
    # intelmodular intelmodular
    # ipdu         ipdu
    # ipmilan      ipmilan
    # ldom         ldom
    # lpar         lpar
    # mcdata       mcdata
    #              netio
    #              ovh
    # rackswitch   rackswitch
    # rhevm        rhevm
    # rsa          rsa
    # rsb          rsb
    # sanbox2      sanbox2
    # virsh        virsh
    # vixel        vixel
    # vmware       vmware
    # vmware_soap  vmware_soap
    # wti          wti
    # xenapi       xenapi
    # zvm          zvm
    artefact_cond('@passwd_script', kind='S',
                  desc='FA: script to retrieve password')
    ) + (
    #  #el6          #el7
    #  alom          alom
    #  apc           apc
    #  apc_snmp      apc_snmp
    #  bladecenter   bladecenter
    #                brocade
    #   cisco_mds    cisco_mds
    #   cisco_ucs    cisco_ucs
    #   drac         drac
    #   drac5        drac5
    #                dummy
    #   eaton_snmp   eaton_snmp
    #   eps          eps
    #                hds_cb
    #   hpblade      hpblade
    #   ibmblade     ibmblade
    #   ifmib        ifmib
    #   ilo          ilo
    #   ilo_mp       ilo_mp
    #   intelmodular intelmodular
    #   ipdu         ipdu
    #   ldom         ldom
    #   lpar         lpar
    #                netio
    #                ovh
    #   rhevm        rhevm
    #   rsa          rsa
    #   rsb          rsb
    #   sanbox2      sanbox2
    #   virsh        virsh
    #   virt         virt
    #   vmware       vmware
    #   vmware_soap  vmware_soap
    #   wti          wti
    #   xenapi       xenapi
    #   xvm          xvm
    artefact_cond('@debug', kind='L',
                  desc='FA: log file with debug information')
    ) + (
    # #el6      #el7
    # virt      virt
    # xvm       xvm
    artefact_cond('@key_file', kind='S',
                  desc='FA: shared key file')
    )

ccs_artefacts = artefact("concat('/usr/sbin/', @agent)", kind='X',
                         desc='fence agent') + ccs_artefacts_common_params
