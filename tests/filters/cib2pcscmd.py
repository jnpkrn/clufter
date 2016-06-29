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
pcs constraint ticket add my-ticket Master my-res loss-policy=demote id=ticket-my-ticket-my-res
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
