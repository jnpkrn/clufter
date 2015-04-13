# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing `cib2pcscmd' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
flt = 'cib2pcscmd'
cib2pcscmd = FilterManager.init_lookup(flt).filters[flt]
cib = cib2pcscmd.in_format


class FiltersCib2pcscmdTestCase(TestCase):
    def testConversion(self):
        in_obj = cib('file', join(dirname(dirname(__file__)), 'filled.cib'))
        ret = cib2pcscmd(in_obj)
        #print ret.BYTESTRING()
        self.assertEquals(
            ret.BYTESTRING(),
            '''\
pcs stonith create FENCEDEV-fence-virt-063 fence_xvm 'auth=sha256' 'hash=sha256' 'key_file=/etc/cluster/fence_xvm.key' 'timeout=5' 'pcmk_host_map=virt-063:virt-063.cluster-qe.lab.eng.brq.redhat.com'
pcs stonith create FENCEDEV-fence-virt-064 fence_xvm 'auth=sha256' 'hash=sha256' 'key_file=/etc/cluster/fence_xvm.key' 'timeout=5' 'pcmk_host_map=virt-064:virt-064.cluster-qe.lab.eng.brq.redhat.com'
pcs stonith create FENCEDEV-fence-virt-069 fence_xvm 'auth=sha256' 'hash=sha256' 'key_file=/etc/cluster/fence_xvm.key' 'timeout=5' 'pcmk_host_map=virt-069:virt-069.cluster-qe.lab.eng.brq.redhat.com'
pcs resource create RESOURCE-ip-10.34.71.234 ocf:heartbeat:IPaddr2 'ip=10.34.71.234'
pcs resource create RESOURCE-apache-webserver ocf:heartbeat:apache 'configfile=/etc/httpd/sconf/httpd.conf' 'options= -Dwebserver -d "/etc/httpd"'
pcs group add SERVICE-svc-GROUP RESOURCE-ip-10.34.71.234 RESOURCE-apache-webserver
'''
        )

from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
