# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing `ccsflat2cibprelude' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_com'))

from os.path import dirname, join, split
from sys import modules

flt = 'ccsflat2cibprelude'

def rewrite_root(flt, new_root):
    # /foo/bar -> (/foo, bar)
    # /foo/bar/ -> (/foo/bar, )
    new_root_dir, new_xml_root = split(new_root)
    old_root_dir = dirname(modules[flt.__class__.__module__].__file__)
    new_root_dir = join(old_root_dir, new_root_dir)
    flt._fnc = (lambda orig_fnc:
        lambda *args, **kwargs: orig_fnc(*args, root_dir=new_root_dir,
                                                xml_root=new_xml_root, **kwargs)
    )(flt._fnc)
    return flt


class FiltersCcsFlat2CibPreludeTestCase(TeardownFilterTestCase):
    def testNfsClient(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt], 'cluster/rm')
        in_fmt, out_fmt = flt_obj.in_format, flt_obj.out_format
        io_strings = (
            ('''\
<nfsclient name="test1" target="*" path="/srv/nfs/test1"/>
''', '''\
<primitive id="RESOURCE-nfsclient-test1" description="natively converted from nfsclient RA" class="ocf" provider="heartbeat" type="exportfs">
  <instance_attributes id="RESOURCE-nfsclient-test1-ATTRS">
    <nvpair id="RESOURCE-nfsclient-test1-ATTRS-clientspec" name="clientspec" value="*"/>
    <nvpair id="RESOURCE-nfsclient-test1-ATTRS-directory" name="directory" value="/srv/nfs/test1"/>
    <!-- NOTE: explicitly disabling unlock_on_stop parameter so as to preserve original behavior; you may want to enable it, though -->
    <nvpair id="RESOURCE-nfsclient-test1-ATTRS-unlock_on_stop" name="unlock_on_stop" value="false"/>
  </instance_attributes>
  <meta_attributes id="RESOURCE-nfsclient-test1-META">
    <nvpair id="RESOURCE-nfsclient-test1-META-service" name="rgmanager-service" value="RESOURCES-"/>
  </meta_attributes>
</primitive>
'''),
            ('''\
<nfsclient name="test2" target="*" path="/srv/nfs/test2" options="rw,async,no_root_squash"/>
''', '''\
<primitive id="RESOURCE-nfsclient-test2" description="natively converted from nfsclient RA" class="ocf" provider="heartbeat" type="exportfs">
  <instance_attributes id="RESOURCE-nfsclient-test2-ATTRS">
    <nvpair id="RESOURCE-nfsclient-test2-ATTRS-clientspec" name="clientspec" value="*"/>
    <nvpair id="RESOURCE-nfsclient-test2-ATTRS-directory" name="directory" value="/srv/nfs/test2"/>
    <nvpair id="RESOURCE-nfsclient-test2-ATTRS-options" name="options" value="rw,async,no_root_squash"/>
    <!-- NOTE: explicitly disabling unlock_on_stop parameter so as to preserve original behavior; you may want to enable it, though -->
    <nvpair id="RESOURCE-nfsclient-test2-ATTRS-unlock_on_stop" name="unlock_on_stop" value="false"/>
  </instance_attributes>
  <meta_attributes id="RESOURCE-nfsclient-test2-META">
    <nvpair id="RESOURCE-nfsclient-test2-META-service" name="rgmanager-service" value="RESOURCES-"/>
  </meta_attributes>
</primitive>
'''),
        )
        for (in_str, out_str) in io_strings:
            in_str = '''\
<rm>
    <resources>
''' + in_str + '''\
    </resources>
</rm>
'''
            in_obj = in_fmt('bytestring', in_str)
            out_obj = flt_obj(in_obj)
            #print out_obj.BYTESTRING()
            self.assertEquals(out_obj.BYTESTRING(), out_str)

from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
