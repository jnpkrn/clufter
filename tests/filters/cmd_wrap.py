# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing `cmd-wrap' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from os.path import dirname, join
from unittest import TestCase

from .filter_manager import FilterManager
from .formats.string_iter import string_iter

flt = 'cmd-wrap'
cmd_wrap = FilterManager.init_lookup(flt).filters[flt]


class FiltersCmdWrapTestCase(TestCase):
    def testCmdWrap60(self):
        result = cmd_wrap(string_iter('stringiter', """\
# this is a long long long long long long long long, terribly long shell comment
/usr/bin/python setup.py saveopts -f setup.cfg pkg_prepare --editor=/usr/bin/vim
""".splitlines()
        ), text_width=60)
        #print result.BYTESTRING()
        self.assertEquals(result.BYTESTRING(), """\
# this is a long long long long long long long long,
# terribly long shell comment
/usr/bin/python setup.py saveopts -f setup.cfg pkg_prepare \\
  --editor /usr/bin/vim
""")


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
