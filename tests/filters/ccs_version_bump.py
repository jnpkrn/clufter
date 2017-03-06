# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `ccs-version-bump' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
flt = 'ccs-version-bump'
ccs_version_bump = FilterManager.init_lookup(flt).filters[flt]
ccs = ccs_version_bump.in_format


class FiltersCcsVersionBumpTestCase(TestCase):
    def testVersionBump(self):
        in_obj = ccs('file', join(dirname(dirname(__file__)), 'filled.conf'))
        ret = ccs_version_bump(in_obj)
        #print(ret.BYTESTRING())
        old_ver = int(in_obj.ETREE().xpath("/cluster/@config_version")[0])
        new_ver = int(ret.ETREE().xpath("/cluster/@config_version")[0])
        self.assertEquals(old_ver + 1, new_ver)

from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
