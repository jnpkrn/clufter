# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
from os.path import dirname, join
from os import remove, stat
#from pprint import pprint

import _bootstrap  # known W402, required

from clufter.command import Command, CommandError

from clufter.filters.ccs2ccsflat import ccs2ccsflat
from clufter.filters.ccsflat2pcs import ccsflat2pcs
from clufter.filters.ccs2coro import ccs2needlexml

from clufter.format import formats
formats = formats.plugins


class ChainResolve(unittest.TestCase):
    def testShapeAndProtocolMatch(self):
        from tempfile import mktemp
        filters = dict(
            ccs2ccsflat=ccs2ccsflat(formats),
            ccsflat2pcs=ccsflat2pcs(formats),
            ccs2needlexml=ccs2needlexml(formats),
        )
        testfile = join(dirname(__file__), 'empty.conf')
        testoutput = mktemp(prefix='out', suffix='.conf',
                            dir=join(dirname(__file__), 'tmp'))

        @Command.deco(('ccs2ccsflat',
                          ('ccsflat2pcs'),
                          ('ccs2needlexml')))
        def cmd_chain_match_01(cmd_ctxt,
                               input=testfile,
                               output=testoutput,
                               coro='.coro'):
            return (
                ('file', input),
                (
                    ('file', output),
                    ('file', coro)
                )
            )
        @Command.deco(('ccs2ccsflat'))
        def cmd_chain_match_02(cmd_ctxt,
                               input=testfile,
                               output=testoutput,
                               coro='.coro'):
            return (
                ('file', input),
                ('file', output)
            )
        @Command.deco(('ccs2ccsflat'))
        def cmd_chain_nonmatch_01(cmd_ctxt,
                                  input=testfile,
                                  output=testoutput,
                                  coro='.coro'):
            return (
                ('file', input),
                (
                    ('file', output),
                    ('file', coro)
                )
            )
        @Command.deco(('ccs2ccsflat',
                          ('ccsflat2pcs'),
                          ('ccs2needlexml'),
                          ('ccs2needlexml')))
        def cmd_chain_nonmatch_02(cmd_ctxt,
                                  input=testfile,
                                  output=testoutput,
                                  coro='.coro'):
            return (
                ('file', input),
                (
                    ('file', output),
                    ('file', coro)
                )
            )
        # malformed protocol name
        @Command.deco(('ccs2ccsflat',
                          ('ccsflat2pcs'),
                          ('ccs2needlexml')))
        def cmd_chain_nonmatch_03(cmd_ctxt,
                                  input=testfile,
                                  output=testoutput,
                                  coro='.coro'):
            return (
                ('file', input),
                (
                    ('file', output),
                    ('life', coro)
                )
            )
        cmd_classes = (
            cmd_chain_match_01,
            cmd_chain_match_02,
            cmd_chain_nonmatch_01,
            cmd_chain_nonmatch_02,
            cmd_chain_nonmatch_03
        )
        split = cmd_classes.index(cmd_chain_nonmatch_01)
        for i, cmd_cls in enumerate(cmd_classes):
            try:
                ret = cmd_cls(filters)({}, [])  # no args/kwargs
                self.assertTrue(ret is not None)
            except CommandError as e:
                print "{0}: {1}".format(cmd_cls.name, e)
                self.assertFalse(i < split)
            except Exception as e:
                print "{0}: {1}".format(cmd_cls.name, e)
                self.assertTrue(i < split)
                raise
            else:
                self.assertTrue(i < split)
                # also test non-zero-size output whe
                self.assertTrue(stat(testoutput).st_size > 0)
                remove(testoutput)
            continue


if __name__ == '__main__':
    unittest.main()
