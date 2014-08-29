# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing direct command run (e.g., when clufter used as a library)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
from os.path import dirname, exists, join
from os import unlink

import _bootstrap

from clufter.command_manager import CommandManager


class Main(unittest.TestCase):
    def testCcs2PcsNeedle(self):
        testfile = join(dirname(__file__), 'filled.conf')
        testcib = join(dirname(__file__), '.testcib.xml')
        testcoro = join(dirname(__file__), '.testcorosync.conf')

        files = dict(
            cib=testcib,
            coro=testcoro,
        )
        clufter_args = type("cluster_args", (object, ), dict(
            input=testfile,
            nocheck=True,
            batch=True,
            **files)
        )
        for f in files.itervalues():
            try:
                unlink(f)
            except OSError:
                pass
        cmd_manager = CommandManager.implicit()
        self.assertFalse(cmd_manager.commands["ccs2pcs-needle"](clufter_args))
        # just the existence of the files is enough for now...
        map(lambda f: self.assertTrue(exists(f)), files.itervalues())


if __name__ == '__main__':
    unittest.main()
