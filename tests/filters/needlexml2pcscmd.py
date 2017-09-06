# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `needlexml2pcscmd' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following makes available also: DeterministicFilterTestCase, rewrite_root
from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_com')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from .filter_manager import FilterManager
from .utils_2to3 import bytes_enc, str_enc
flt = 'needlexml2pcscmd'


class FiltersNeedlexml2pcscmdBasicTestCase(DeterministicFilterTestCase):
    def testClusterSetup(self):
        flt_obj = self.flt_mgr.filters[flt]
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<corosync>
    <totem version="2" transport="udpu"/>
    <nodelist>
        <node nodeid="1" ring0_addr="node1"/>
        <node nodeid="2" ring0_addr="node2"/>
        <node nodeid="3" ring0_addr="node3"/>
    </nodelist>
</corosync>
''', '''\
pcs cluster setup --name _NEEDED_ node1 node2 node3 --transport udpu
pcs cluster start --all --wait=60
'''),
        )
        for (in_str, out_str) in io_strings:
            in_obj = in_fmt('bytestring', bytes_enc(in_str),
                            validator_specs={in_fmt.ETREE: ''})
            # there may be issues with this when tests (ever?) run in parallel
            out_obj = flt_obj(in_obj, pcscmd_verbose=False, pcscmd_tmpcib='',
                              pcscmd_noauth=True, pcscmd_noguidance=True,
                              system='linux', system_extra=('rhel', '7.3'))
            #print(out_obj.BYTESTRING())
            self.assertEqual(str_enc(out_obj.BYTESTRING()), out_str)


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
