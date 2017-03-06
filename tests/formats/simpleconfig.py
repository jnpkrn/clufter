# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing simpleconfig format"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))

from unittest import TestCase

from .format_manager import FormatManager
from .utils_2to3 import bytes_enc

simpleconfig = FormatManager.init_lookup('simpleconfig').formats['simpleconfig']


class FormatsSimpleConfigTestCase(TestCase):

    bytestring = bytes_enc("""\
nodelist {
	node {
		nodeid: 1
		ring0_addr: virt-063
	}
	node {
		nodeid: 2
		ring0_addr: virt-064
	}
	node {
		nodeid: 3
		ring0_addr: virt-069
	}
}
quorum {
	provider: corosync_votequorum
}
totem {
	cluster_name: STSRHTS29624
	consensus: 600
	join: 60
	key: _NOT_SECRET--f646V_a6vNwwvqYSy4cYSxPp1DizBakKJ9UULEAXswc
	token: 3000
	version: 2
}
""")

    struct = \
        ('',
          [],
          [('nodelist',
            [],
            [('node', [('nodeid', '1'), ('ring0_addr', 'virt-063')], []),
             ('node', [('nodeid', '2'), ('ring0_addr', 'virt-064')], []),
             ('node', [('nodeid', '3'), ('ring0_addr', 'virt-069')], [])]),
           ('quorum', [('provider', 'corosync_votequorum')], []),
           ('totem',
            [('cluster_name', 'STSRHTS29624'),
             ('consensus', '600'),
             ('join', '60'),
             ('key', '_NOT_SECRET--f646V_a6vNwwvqYSy4cYSxPp1DizBakKJ9UULEAXswc'),
             ('token', '3000'),
             ('version', '2')],
            [])]
        )

    def testStruct2Bytestring(self):
        sc = simpleconfig('struct', self.struct)
        #print(sc.BYTESTRING())
        self.assertEqual(sc.BYTESTRING(), self.bytestring)

    def testBytestring2Struct(self):
        sc = simpleconfig('bytestring', self.bytestring)
        #from pprint import pprint
        #pprint(sc.STRUCT())
        self.assertEqual(sc.STRUCT(), self.struct)


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
