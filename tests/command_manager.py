# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing command manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


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
        #print(commands)
        for cls in (ccs2pcs_needle, ):
            self.assertTrue(cls.name in commands)
            self.assertEqual(cls, type(commands[cls.name]))


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
