# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing direct command run (e.g., when clufter used as a library)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase
from os.path import dirname, exists, join
#from os import unlink

from .command_manager import CommandManager
from .utils_2to3 import iter_values
from .utils_func import foreach


class Main(TestCase):
    #def testCcs2PcsNeedle(self):
    #    testfile = join(dirname(__file__), 'filled.conf')
    #    testcib = join(dirname(__file__), '.testcib.xml')
    #    testcoro = join(dirname(__file__), '.testcorosync.conf')

    #    outputs = dict(
    #        cib=testcib,
    #        coro=testcoro,
    #    )
    #    clufter_args = type("cluster_args", (object, ), dict(
    #        input=testfile,
    #        nocheck=True,
    #        batch=True,
    #        **outputs)
    #    )
    #    for o in outputs:
    #        try:
    #            unlink(outputs[o])
    #        except OSError:
    #            pass
    #    cmd_manager = CommandManager.implicit()
    #    self.assertFalse(cmd_manager.commands["ccs2pcs-needle"](clufter_args))
    #    # just the existence of the files is enough for now...
    #    foreach(lambda f: self.assertTrue(exists(f)), iter_values(outputs))

    def testCcs2PcsNeedleBetter(self):
        testfile = join(dirname(__file__), 'filled.conf')
        from .formats.simpleconfig import simpleconfig
        #from clufter.protocol import protocols
        #protocols = protocols.plugins

        outputs = {
            # alternatives for posterity:
            #"cib" : {'passin': protocols['bytestring']},
            #"cib" : {'passin': 'bytestring'},
            "cib" : {'passin': simpleconfig.BYTESTRING},
            "coro": {'passin': simpleconfig.STRUCT},
        }
        clufter_args = type("cluster_args", (object, ), dict(
            input=testfile,
            nocheck=True,
            batch=True,
            **outputs)
        )
        # alternatively:
        #commands = CommandManager.lookup('ccs2pcs-needle')
        #cmd_manager = CommandManager(plugins=commands, paths=None)
        #cmd = cmd_manager.commands['ccs2pcs-needle']
        cmd = CommandManager.init_lookup('ccs2pcs').commands['ccs2pcs-needle']
        self.assertFalse(cmd(clufter_args))
        # just the existence of non-null strings is enough for now...
        foreach(lambda fsp: self.assertTrue(fsp['passout']), iter_values(outputs))
        #from pprint import pprint
        #pprint(outputs['coro']['passout'])


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
