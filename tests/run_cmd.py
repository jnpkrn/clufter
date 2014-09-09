# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing direct command run (e.g., when clufter used as a library)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os.path as op; execfile(op.join(op.dirname(__file__), '_bootstrap.py'))


from unittest import TestCase
from os.path import dirname, exists, join
#from os import unlink

from .command_manager import CommandManager


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
    #    for f in outputs.itervalues():
    #        try:
    #            unlink(f)
    #        except OSError:
    #            pass
    #    cmd_manager = CommandManager.implicit()
    #    self.assertFalse(cmd_manager.commands["ccs2pcs-needle"](clufter_args))
    #    # just the existence of the files is enough for now...
    #    map(lambda f: self.assertTrue(exists(f)), outputs.itervalues())

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
        map(lambda fspec: self.assertTrue(fspec['passout']), outputs.values())
        #from pprint import pprint
        #pprint(outputs['coro']['passout'])


execfile(op.join(op.dirname(__file__), '_bootstart.py'))
