# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
from os.path import dirname, join
from os import remove
#from pprint import pprint

import _bootstrap  # known W402, required

from clufter.command import Command, CommandError

from clufter.filters.ccs2ccsflat import ccs2ccsflat
from clufter.filters.ccsflat2pcs import ccsflat2pcs
from clufter.filters.ccs2coro import ccs2needlexml

from clufter.formats.ccs import ccs, ccsflat
from clufter.formats.coro import coroxml
from clufter.formats.pcs import pcs

from clufter.utils_func import apply_preserving_depth, \
                               apply_aggregation_preserving_depth


class ChainResolve(unittest.TestCase):
    def testShapeAndProtocolMatch(self):
        from tempfile import mktemp
        filters = dict(
            ccs2ccsflat=ccs2ccsflat(ccs, ccsflat),
            ccsflat2pcs=ccsflat2pcs(ccsflat, pcs),
            ccs2coroxml=ccs2needlexml(ccs, coroxml),
        )
        testfile = join(dirname(__file__), 'empty.conf')
        testoutput = mktemp(prefix='out', suffix='.conf',
                            dir=join(dirname(__file__), 'tmp'))

        #@Command.deco(('ccs2ccsflat',
        #               'ccsflat2pcs', 'ccs2coroxml'))
        #def cmd_chain_match_01(cmd_ctxt,
        #                    input=testfile, output=testoutput, coro='.coro'):
        #    return ('file', input), (('file', output), ('file', coro))
        #@Command.deco(('ccs2ccsflat'))
        #def cmd_chain_match_02(cmd_ctxt,
        #                    input=testfile, output=testoutput, coro='.coro'):
        #    return ('file', input), ('file', output)
        @Command.deco(('ccs2ccsflat'))
        def cmd_chain_nonmatch_01(cmd_ctxt,
                                  input=testfile, output=testoutput,
                                  coro='.coro'):
            return ('file', input), (('file', output), ('file', coro))
        @Command.deco(('ccs2ccsflat',
                       'ccsflat2pcs', 'ccs2coroxml', 'ccs2coroxml'))
        def cmd_chain_nonmatch_02(cmd_ctxt,
                                  input=testfile, output=testoutput,
                                  coro='.coro'):
            return ('file', input), (('file', output), ('file', coro))
        # malformed protocol name
        @Command.deco(('ccs2ccsflat',
                       'ccsflat2pcs', 'ccs2coroxml'))
        def cmd_chain_nonmatch_03(cmd_ctxt,
                                  input=testfile, output=testoutput,
                                  coro='.coro'):
            return ('file', input), (('file', output), ('life', coro))

        cmd_classes = (#cmd_chain_match_01,
                       #cmd_chain_match_02,
                       cmd_chain_nonmatch_01,
                       cmd_chain_nonmatch_02,
                       cmd_chain_nonmatch_03
                       )
        split = cmd_classes.index(cmd_chain_nonmatch_01)
        for i, cmd_cls in enumerate(cmd_classes):
            res_input = cmd_cls.filter_chain
            res_output = apply_preserving_depth(filters.get)(res_input)
            if apply_aggregation_preserving_depth(all)(res_output):
                #log.debug("resolve at `{0}' command: `{1}' -> {2}"
                #          .format(cmd_cls.name, repr(res_input), repr(res_output)))
                try:
                    cmd = cmd_cls(*res_output)
                    cmd({}, [])
                except CommandError as e:
                    print "{0}: {1}".format(cmd_cls.name, e)
                    self.assertFalse(i < split)
                except Exception as e:
                    print "{0}: {1}".format(cmd_cls.name, e)
                    raise
                    self.assertTrue(i < split)
                else:
                    self.assertTrue(i < split)
                try:
                    with open(testfile) as src, open(testoutput) as dst:
                        #self.assertEqual(src.read(), dst.read())
                        pass
                except IOError:
                    pass
                else:
                    remove(testoutput)
                continue
            self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
