# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing `needleqdevicexml2pcscmd' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following makes available also: TeardownFilterTestCase, rewrite_root
from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_com'))


from .filter_manager import FilterManager
flt = 'needleqdevicexml2pcscmd'
cib2pcscmd = FilterManager.init_lookup(flt).filters[flt]
cib = cib2pcscmd.in_format


class FiltersCib2pcscmdQuorumDeviceTestCase(TeardownFilterTestCase):
    def testQuorumDeviceNet(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt], 'corosync/quorum')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<device model="net">
    <net host="191.168.10.20"/>
</device>
''', '''\
pcs quorum device add --help >/dev/null 2>&1 && pcs quorum device add model net host=191.168.10.20
'''),
        )
        for (in_str, out_str) in io_strings:
            in_obj = in_fmt('bytestring', in_str,
                            validator_specs={in_fmt.ETREE: ''})
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='')
            #print out_obj.BYTESTRING()
            self.assertEquals(out_obj.BYTESTRING(), out_str)


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
