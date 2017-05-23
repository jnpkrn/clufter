# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing filters for upgrading CIB formats"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following makes available also: TeardownFilterTestCase, rewrite_root
from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_com')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from .filter_manager import FilterManager
flt = 'fmt-cib-1to2'
fmt_cib_1to2 = FilterManager.init_lookup(flt).filters[flt]
cib1 = fmt_cib_1to2.in_format


class FiltersFmtCib1to2TestCase(TeardownFilterTestCase):
    def testConversion(self):
        in_obj = cib1('bytestring', '''\
<cib validate-with="pacemaker-1.2" epoch="6" num_updates="0" admin_epoch="0">
  <configuration>
    <crm_config>
      <cluster_property_set id="cib-bootstrap-options">
        <nvpair id="cib-bootstrap-options-enable-acl" name="enable-acl" value="true"/>
        <nvpair id="cib-bootstrap-options-stonith-enabled" name="stonith-enabled" value="false"/>
        <nvpair id="cib-bootstrap-options-no-quorum-policy" name="no-quorum-policy" value="freeze"/>
        <nvpair id="cib-bootstrap-options-cluster-infrastructure" name="cluster-infrastructure" value="corosync"/>
        <nvpair id="cib-bootstrap-options-cluster-name" name="cluster-name" value="testsingle"/>
      </cluster_property_set>
    </crm_config>
    <nodes/>
    <resources/>
    <constraints/>
    <acls>
      <acl_user id="fixer">
        <write id="fixer_write_options" ref="cib-bootstrap-options"/>
        <deny id="fixer_deny_aclenabled" ref="cib-bootstrap-options-enable-acl"/>
        <deny id="fixer_deny_stonith" ref="cib-bootstrap-options-stonith-enabled"/>
        <deny id="fixer_deny_noquorum" ref="cib-bootstrap-options-no-quorum-policy"/>
      </acl_user>
    </acls>
  </configuration>
</cib>
''')
        ret = fmt_cib_1to2(in_obj)
        #print(ret.BYTESTRING())
        self.assertEqual(
            ret.BYTESTRING(),
            '''\
<cib validate-with="pacemaker-2.0" epoch="6" num_updates="0" admin_epoch="0">
  <configuration>
    <crm_config>
      <cluster_property_set id="cib-bootstrap-options">
        <nvpair id="cib-bootstrap-options-enable-acl" name="enable-acl" value="true"/>
        <nvpair id="cib-bootstrap-options-stonith-enabled" name="stonith-enabled" value="false"/>
        <nvpair id="cib-bootstrap-options-no-quorum-policy" name="no-quorum-policy" value="freeze"/>
        <nvpair id="cib-bootstrap-options-cluster-infrastructure" name="cluster-infrastructure" value="corosync"/>
        <nvpair id="cib-bootstrap-options-cluster-name" name="cluster-name" value="testsingle"/>
      </cluster_property_set>
    </crm_config>
    <nodes/>
    <resources/>
    <constraints/>
    <acls>
      <acl_target id="fixer">
        <role id="auto-fixer"/>
      </acl_target>
      <acl_role id="auto-fixer">
        <acl_permission id="fixer_write_options" kind="write" reference="cib-bootstrap-options"/>
        <acl_permission id="fixer_deny_aclenabled" kind="deny" reference="cib-bootstrap-options-enable-acl"/>
        <acl_permission id="fixer_deny_stonith" kind="deny" reference="cib-bootstrap-options-stonith-enabled"/>
        <acl_permission id="fixer_deny_noquorum" kind="deny" reference="cib-bootstrap-options-no-quorum-policy"/>
      </acl_role>
    </acls>
  </configuration>
</cib>
'''
        )


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
