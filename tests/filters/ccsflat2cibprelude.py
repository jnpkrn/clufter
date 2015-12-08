# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing `ccsflat2cibprelude' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following makes available also: TeardownFilterTestCase, rewrite_root
from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_com'))

flt = 'ccsflat2cibprelude'

class FiltersCcsFlat2CibPreludeTestCase(TeardownFilterTestCase):
    def testNfsClient(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt], 'cluster/rm')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<nfsclient name="test1" target="*" path="/srv/nfs/test1"/>
''', '''\
<primitive id="RESOURCE-nfsclient-test1" description="natively converted from nfsclient RA" class="ocf" provider="heartbeat" type="exportfs">
  <instance_attributes id="RESOURCE-nfsclient-test1-ATTRS">
    <nvpair id="RESOURCE-nfsclient-test1-ATTRS-clientspec" name="clientspec" value="*"/>
    <nvpair id="RESOURCE-nfsclient-test1-ATTRS-directory" name="directory" value="/srv/nfs/test1"/>
    <!-- NOTE: explicitly disabling `unlock_on_stop` parameter for `exportfs` resource so as to preserve original `nfsclient` resource behavior; you may want to enable it, though -->
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
    <!-- NOTE: explicitly disabling `unlock_on_stop` parameter for `exportfs` resource so as to preserve original `nfsclient` resource behavior; you may want to enable it, though -->
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

    def testSapDatabase(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt], 'cluster/rm')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<SAPDatabase SID="SAP1" DBTYPE="ORA" NETSERVICENAME="LISTENER_SAP1" DIR_EXECUTABLE="/dbpath/SAP1"/>
''', '''\
<primitive id="RESOURCE-SAPDatabase-SAP1" description="natively converted from SAPDatabase RA" class="ocf" provider="heartbeat" type="SAPDatabase">
  <instance_attributes id="RESOURCE-SAPDatabase-SAP1-ATTRS">
    <nvpair id="RESOURCE-SAPDatabase-SAP1-ATTRS-SID" name="SID" value="SAP1"/>
    <nvpair id="RESOURCE-SAPDatabase-SAP1-ATTRS-DBTYPE" name="DBTYPE" value="ORA"/>
    <nvpair id="RESOURCE-SAPDatabase-SAP1-ATTRS-NETSERVICENAME" name="NETSERVICENAME" value="LISTENER_SAP1"/>
  </instance_attributes>
  <meta_attributes id="RESOURCE-SAPDatabase-SAP1-META">
    <nvpair id="RESOURCE-SAPDatabase-SAP1-META-service" name="rgmanager-service" value="RESOURCES-"/>
  </meta_attributes>
</primitive>
'''),
            ('''\
<SAPDatabase SID="GT1" AUTOMATIC_RECOVER="TRUE" DBTYPE="ORA" DIR_EXECUTABLE="/sapmnt/GT1/exe" STRICT_MONITORING="FALSE"/>
''', '''\
<primitive id="RESOURCE-SAPDatabase-GT1" description="natively converted from SAPDatabase RA" class="ocf" provider="heartbeat" type="SAPDatabase">
  <instance_attributes id="RESOURCE-SAPDatabase-GT1-ATTRS">
    <nvpair id="RESOURCE-SAPDatabase-GT1-ATTRS-SID" name="SID" value="GT1"/>
    <nvpair id="RESOURCE-SAPDatabase-GT1-ATTRS-DBTYPE" name="DBTYPE" value="ORA"/>
    <nvpair id="RESOURCE-SAPDatabase-GT1-ATTRS-STRICT_MONITORING" name="STRICT_MONITORING" value="FALSE"/>
    <nvpair id="RESOURCE-SAPDatabase-GT1-ATTRS-AUTOMATIC_RECOVER" name="AUTOMATIC_RECOVER" value="TRUE"/>
  </instance_attributes>
  <meta_attributes id="RESOURCE-SAPDatabase-GT1-META">
    <nvpair id="RESOURCE-SAPDatabase-GT1-META-service" name="rgmanager-service" value="RESOURCES-"/>
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

    def testSapInstance(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt], 'cluster/rm')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<SAPInstance AUTOMATIC_RECOVER="TRUE" DIR_EXECUTABLE="/sapmnt/GT1/exe" InstanceName="GT1_foobar"/>
''', '''\
<primitive id="RESOURCE-SAPInstance-GT1_foobar" description="natively converted from SAPInstance RA" class="ocf" provider="heartbeat" type="SAPInstance">
  <instance_attributes id="RESOURCE-SAPInstance-GT1_foobar-ATTRS">
    <nvpair id="RESOURCE-SAPInstance-GT1_foobar-ATTRS-InstanceName" name="InstanceName" value="GT1_foobar"/>
    <nvpair id="RESOURCE-SAPInstance-GT1_foobar-ATTRS-DIR_EXECUTABLE" name="DIR_EXECUTABLE" value="/sapmnt/GT1/exe"/>
    <nvpair id="RESOURCE-SAPInstance-GT1_foobar-ATTRS-AUTOMATIC_RECOVER" name="AUTOMATIC_RECOVER" value="TRUE"/>
  </instance_attributes>
  <meta_attributes id="RESOURCE-SAPInstance-GT1_foobar-META">
    <nvpair id="RESOURCE-SAPInstance-GT1_foobar-META-service" name="rgmanager-service" value="RESOURCES-"/>
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
