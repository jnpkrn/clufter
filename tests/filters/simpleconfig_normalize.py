# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing `simpleconfig-normalize' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
from .formats.simpleconfig import simpleconfig
from .utils_2to3 import str_enc

flt = 'simpleconfig-normalize'
simpleconfig_normalize = FilterManager.init_lookup(flt).filters[flt]


class FiltersSimpleconfigNormalizeTestCase(TestCase):
    def testSimpleconfigNormalize(self):
        result = simpleconfig_normalize(simpleconfig('struct',
            ('IGNORED',
            [],
            [('uidgid', [('uid', '0'), ('uid', '1000'), ('gid', '0')], [])])
        ))
        #print result.BYTESTRING()
        self.assertEquals(str_enc(result.BYTESTRING(), 'utf-8'), """\
uidgid {
	uid: 0
	gid: 0
}
uidgid {
	uid: 1000
}
""")


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
