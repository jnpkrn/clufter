# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing `cib2pcscmd' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following makes available also: TeardownFilterTestCase, rewrite_root
from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_com'))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
flt = 'cib2pcscmd'
cib2pcscmd = FilterManager.init_lookup(flt).filters[flt]
cib = cib2pcscmd.in_format


class FiltersCib2pcscmdTestCase(TestCase):
    def testConversion(self):
        in_obj = cib('file', join(dirname(dirname(__file__)), 'filled.cib'))
        ret = cib2pcscmd(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='')
        #print ret.BYTESTRING()
        self.assertEquals(
            ret.BYTESTRING(),
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
            in_obj = in_fmt('bytestring', in_str,
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='')
            #print out_obj.BYTESTRING()
            self.assertEquals(out_obj.BYTESTRING(), out_str)

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
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<constraints>
''' + in_str + '''
</constraints>
'''
            in_obj = in_fmt('bytestring', in_str,
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='')
            #print out_obj.BYTESTRING()
            self.assertEquals(out_obj.BYTESTRING(), out_str)

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
            in_obj = in_fmt('bytestring', in_str,
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='')
            #print out_obj.BYTESTRING()
            self.assertEquals(out_obj.BYTESTRING(), out_str)

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
            in_obj = in_fmt('bytestring', in_str,
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='')
            #print out_obj.BYTESTRING()
            self.assertEquals(out_obj.BYTESTRING(), out_str)


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
