# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `cib2pcscmd' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following makes available also: TeardownFilterTestCase, rewrite_root
from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_com')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
from .utils_2to3 import bytes_enc, str_enc
flt = 'cib2pcscmd'
cib2pcscmd = FilterManager.init_lookup(flt).filters[flt]
cib = cib2pcscmd.in_format


class FiltersCib2pcscmdTestCase(TestCase):
    def testConversion(self):
        in_obj = cib('file', join(dirname(dirname(__file__)), 'filled.cib'))
        ret = cib2pcscmd(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                         system='linux', system_extra=('rhel', '7.3'))
        #print(ret.BYTESTRING())
        self.assertEqual(
            str_enc(ret.BYTESTRING()),
            '''\
pcs stonith create FENCEDEV-fence-virt-063 fence_xvm 'auth=sha256' 'hash=sha256' 'key_file=/etc/cluster/fence_xvm.key' 'timeout=5' 'pcmk_host_map=virt-063:virt-063.example.com'
pcs stonith create FENCEDEV-fence-virt-064 fence_xvm 'auth=sha256' 'hash=sha256' 'key_file=/etc/cluster/fence_xvm.key' 'timeout=5' 'pcmk_host_map=virt-064:virt-064.example.com'
pcs stonith create FENCEDEV-fence-virt-069 fence_xvm 'auth=sha256' 'hash=sha256' 'key_file=/etc/cluster/fence_xvm.key' 'timeout=5' 'pcmk_host_map=virt-069:virt-069.example.com'
pcs resource create RESOURCE-ip-10.34.71.234 ocf:heartbeat:IPaddr2 'ip=10.34.71.234'
pcs resource create RESOURCE-apache-webserver ocf:heartbeat:apache 'configfile=/etc/httpd/sconf/httpd.conf' 'options= -Dwebserver -d "/etc/httpd"'
pcs resource create memcached systemd:memcached op start 'interval=0s' 'timeout=60s' monitor 'interval=60s'
pcs resource group add SERVICE-svc-GROUP RESOURCE-ip-10.34.71.234 RESOURCE-apache-webserver
pcs resource clone memcached 'interleave=true'
'''
        )


class FiltersCib2pcscmdConstraintsTestCase(TeardownFilterTestCase):
    def testColocationConstraints(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/constraints')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<rsc_colocation id="colocation-A-with-B" rsc="A" with-rsc="B" score="INFINITY"/>
''', '''\
pcs constraint colocation add A with B id=colocation-A-with-B
'''),
            ('''\
<rsc_colocation id="colocation-A-with-B" rsc="A" with-rsc="B"/>
''', '''\
pcs constraint colocation add A with B 0 id=colocation-A-with-B
'''),
            ('''\
<rsc_colocation id="colocation-A-with-B" rsc="A" with-rsc="B" with-rsc-role="Master" score="INFINITY"/>
''', '''\
pcs constraint colocation add A with master B id=colocation-A-with-B
'''),
            ('''\
<rsc_colocation id="colocation-my-rsc-set">
    <resource_set id="my-rsc-set">
        <resource_ref id="my-res-1"/>
        <resource_ref id="my-res-2"/>
    </resource_set>
</rsc_colocation>
''', '''\
pcs constraint colocation set my-res-1 my-res-2 \
setoptions id=colocation-my-rsc-set
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<constraints>
''' + in_str + '''
</constraints>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.3'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)

    def testLocationConstraints(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/constraints')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<rsc_location id="location-A-on-X" rsc="A" node="X" score="INFINITY"/>
''', '''\
pcs constraint location A prefers X
'''),
            ('''\
<rsc_location id="location-A-on-X" rsc="A" node="X" score="-INFINITY"/>
''', '''\
pcs constraint location A avoids X
'''),
            ('''\
<rsc_location id="location-A-on-XYZ" rsc="A">
    <rule id="location-X-on-XYZ-rule" boolean-op="or" score="INFINITY">
        <expression id="location-X-on-XYZ-expr-X" attribute="#uname"
                    operation="eq" value="X"/>
        <expression id="location-X-on-XYZ-expr-Y" attribute="#uname"
                    operation="eq" value="Y"/>
        <expression id="location-X-on-XYZ-expr-Z" attribute="#uname"
                    operation="eq" value="Z"/>
    </rule>
</rsc_location>
''', '''\
pcs constraint location A rule id=location-X-on-XYZ-rule \
constraint-id=location-A-on-XYZ score=INFINITY \
'#uname' eq 'X' or '#uname' eq 'Y' or '#uname' eq 'Z'
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<constraints>
''' + in_str + '''
</constraints>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.3'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)

    def testOrderConstraints(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/constraints')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<rsc_order id="order-A-then-B" first="A" then="B"/>
''', '''\
pcs constraint order A then B id=order-A-then-B
'''),
            ('''\
<rsc_order id="order-A-then-B" first="A" then="B" kind="Mandatory"/>
''', '''\
pcs constraint order A then B kind=Mandatory id=order-A-then-B
'''),
            ('''\
<rsc_order id="order-my-rsc-set">
    <resource_set id="my-rsc-set">
        <resource_ref id="my-res-1"/>
        <resource_ref id="my-res-2"/>
    </resource_set>
</rsc_order>
''', '''\
pcs constraint order set my-res-1 my-res-2 setoptions id=order-my-rsc-set
'''),
            ('''\
<rsc_order id="order-my-rsc-set">
    <resource_set id="my-rsc-set" sequential="false">
        <resource_ref id="my-res-1"/>
        <resource_ref id="my-res-2"/>
    </resource_set>
</rsc_order>
''', '''\
pcs constraint order set my-res-1 my-res-2 sequential=false \
setoptions id=order-my-rsc-set
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<constraints>
''' + in_str + '''
</constraints>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.3'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)

    def testTicketConstraints(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/constraints')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<rsc_ticket id="ticket-my-ticket-my-res" rsc="my-res" ticket="my-ticket"/>
''', '''\
pcs constraint ticket add my-ticket my-res id=ticket-my-ticket-my-res
'''),
            ('''\
<rsc_ticket id="ticket-my-ticket-my-res" rsc="my-res" rsc-role="Master"
            ticket="my-ticket" loss-policy="demote"/>
''', '''\
pcs constraint ticket add my-ticket Master my-res loss-policy=demote \
id=ticket-my-ticket-my-res
'''),
            ('''\
<rsc_ticket id="ticket-my-ticket-my-rsc-set" ticket="my-ticket">
    <resource_set id="my-rsc-set">
        <resource_ref id="my-res-1"/>
        <resource_ref id="my-res-2"/>
    </resource_set>
</rsc_ticket>
''', '''\
pcs constraint ticket set my-res-1 my-res-2 setoptions ticket=my-ticket \
id=ticket-my-ticket-my-rsc-set
'''),
            ('''\
<rsc_ticket id="ticket-my-ticket-my-rsc-set" ticket="my-ticket"
             loss-policy="fence">
    <resource_set id="my-rsc-set-1" role="Started">
        <resource_ref id="my-res-1"/>
    </resource_set>
    <resource_set id="my-rsc-set-2" role="Master">
        <resource_ref id="my-res-2"/>
    </resource_set>
</rsc_ticket>
''', '''\
pcs constraint ticket set my-res-1 role=Started set my-res-2 role=Master \
setoptions ticket=my-ticket loss-policy=fence id=ticket-my-ticket-my-rsc-set
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<constraints>
''' + in_str + '''
</constraints>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.3'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)


class FiltersCib2pcscmdAlertsTestCase(TeardownFilterTestCase):
    def testAlertsSimple(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/alerts')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<alert id="alert-foo" path="/bin/true"/>
''', '''\
pcs alert create 'path=/bin/true' id=alert-foo
'''),
            ('''\
<alert id="alert-bar" path="/bin/yes" description="idling avoidance ;-)"/>
''', '''\
pcs alert create 'path=/bin/yes' id=alert-bar 'description=idling avoidance ;-)'
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<alerts>
''' + in_str + '''
</alerts>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.3'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)

    def testAlertsComplex(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/alerts')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<alert id="alert-foo" path="/bin/true">
    <recipient id="alert-foo-recipient1" description="first!!1" value="1"/>
    <recipient id="alert-foo-recipient2" value="2"/>
    <recipient id="alert-foo-recipient3" value="3"/>
</alert>
''', '''\
pcs alert create 'path=/bin/true' id=alert-foo
pcs alert recipient add alert-foo 'value=1' id=alert-foo-recipient1 'description=first!!1'
pcs alert recipient add alert-foo 'value=2' id=alert-foo-recipient2
pcs alert recipient add alert-foo 'value=3' id=alert-foo-recipient3
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<alerts>
''' + in_str + '''
</alerts>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.3'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)


class FiltersCib2pcscmdACLTestCase(TeardownFilterTestCase):
    def testACLSimple(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/acls')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<acl_role id="no-fd-passwd">
  <acl_permission id="no-fd-passwd-perm" kind="deny" reference="no-fd-passwd"/>
</acl_role>
<acl_target id="observer">
  <role id="no-fd-passwd"/>
</acl_target>
''', '''\
pcs acl role create no-fd-passwd deny id no-fd-passwd
pcs acl user create observer no-fd-passwd
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<acls>
''' + in_str + '''
</acls>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.3'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)


class FiltersCib2pcscmdBundleTestCase(TeardownFilterTestCase):
    def testBundleSimple(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/resources')
        in_fmt = flt_obj.in_format
        io_strings = (
            # see http://wiki.clusterlabs.org/wiki/Bundle_Walk-Through#Configure_the_cluster
            ('''\
<bundle id="httpd-bundle">
  <docker image="pcmktest:http" replicas="3" options="--log-driver=journald" />
  <network ip-range-start="192.168.122.131" host-interface="eth0" host-netmask="24">
    <port-mapping id="httpd-port" port="80"/>
  </network>
  <storage>
    <storage-mapping id="httpd-root"
      source-dir-root="/var/local/containers"
      target-dir="/var/www/html"
      options="rw"/>
    <storage-mapping id="httpd-logs"
      source-dir-root="/var/log/pacemaker/bundles"
      target-dir="/etc/httpd/logs"
      options="rw"/>
  </storage>
  <primitive class="ocf" id="httpd" provider="heartbeat" type="apache"/>
</bundle>
''', '''\
pcs resource bundle create httpd-bundle container docker 'image=pcmktest:http' 'replicas=3' 'options=--log-driver=journald' network  'ip-range-start=192.168.122.131' 'host-interface=eth0' 'host-netmask=24' port-map  'id=httpd-port' 'port=80' storage-map  'id=httpd-root' 'source-dir-root=/var/local/containers' 'target-dir=/var/www/html' 'options=rw' storage-map  'id=httpd-logs' 'source-dir-root=/var/log/pacemaker/bundles' 'target-dir=/etc/httpd/logs' 'options=rw'
pcs resource create httpd ocf:heartbeat:apache bundle httpd-bundle
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<resources>
''' + in_str + '''
</resources>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.4'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)

    def testBundleMeta(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt],
                               'cib/configuration/resources')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<bundle id="httpd-bundle">
  <docker image="pcmktest:http" replicas="3" options="--log-driver=journald" />
  <network ip-range-start="192.168.122.131" host-interface="eth0" host-netmask="24">
    <port-mapping id="httpd-port" port="80"/>
  </network>
  <storage>
    <storage-mapping id="httpd-root"
      source-dir-root="/var/local/containers"
      target-dir="/var/www/html"
      options="rw"/>
    <storage-mapping id="httpd-logs"
      source-dir-root="/var/log/pacemaker/bundles"
      target-dir="/etc/httpd/logs"
      options="rw"/>
  </storage>
  <meta_attributes id="httpd-bundle-META">
    <nvpair id="httpd-bundle-META-" name="is-managed" value="false"/>
  </meta_attributes>
  <primitive class="ocf" id="httpd" provider="heartbeat" type="apache"/>
</bundle>
''', '''\
pcs resource bundle create httpd-bundle container docker 'image=pcmktest:http' 'replicas=3' 'options=--log-driver=journald' network  'ip-range-start=192.168.122.131' 'host-interface=eth0' 'host-netmask=24' port-map  'id=httpd-port' 'port=80' storage-map  'id=httpd-root' 'source-dir-root=/var/local/containers' 'target-dir=/var/www/html' 'options=rw' storage-map  'id=httpd-logs' 'source-dir-root=/var/log/pacemaker/bundles' 'target-dir=/etc/httpd/logs' 'options=rw' meta 'is-managed=false'
pcs resource create httpd ocf:heartbeat:apache bundle httpd-bundle
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<resources>
''' + in_str + '''
</resources>
'''
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              system='linux', system_extra=('rhel', '7.5'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
