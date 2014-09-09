# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing command manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os.path as op; execfile(op.join(op.dirname(__file__), '_bootstrap.py'))


from unittest import TestCase

from .command_manager import CommandManager
from .commands.ccs2pcs import ccs2pcs_needle


class CommandManagerTestCase(TestCase):
    def setUp(self):
        self.cmd_mgr = CommandManager.init_lookup()

    def tearDown(self):
        self.cmd_mgr.registry.setup(True)  # start from scratch
        self.cmd_mgr = None


class Default(CommandManagerTestCase):
    def test_default(self):
        commands = self.cmd_mgr.commands
        #print commands
        for cls in (ccs2pcs_needle, ):
            self.assertTrue(cls.name in commands)
            self.assertEqual(cls, type(commands[cls.name]))


execfile(op.join(op.dirname(__file__), '_bootstart.py'))
