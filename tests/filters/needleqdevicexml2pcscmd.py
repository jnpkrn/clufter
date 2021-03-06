# -*- coding: UTF-8 -*-
# Copyright 2018 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `needleqdevicexml2pcscmd' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following makes available also: TeardownFilterTestCase, rewrite_root
from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_com')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from .filter_manager import FilterManager
from .utils_2to3 import bytes_enc, str_enc
flt = 'needleqdevicexml2pcscmd'


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
pcs quorum device add model net host=191.168.10.20
'''), ('''\
<device model="net">
    <net host="191.168.10.20" tls="required"/>
    <heuristics mode="on" timeout="5" sync_timeout="15" interval="30"
                exec_ping="ping -q -c 1 127.0.0.1"/>
</device>
''', '''\
pcs quorum device add model net host=191.168.10.20 heuristics mode=on timeout=5 sync_timeout=15 interval=30 'exec_ping=ping -q -c 1 127.0.0.1'
'''),
        )
        for (in_str, out_str) in io_strings:
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
