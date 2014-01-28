# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import unittest
#from pprint import pprint

import _bootstrap  # known W402, required

from clufter.command import Command, CommandError

from clufter.filters.ccs2ccsflat import ccs2ccsflat
from clufter.filters.ccsflat2pcs import ccsflat2pcs
from clufter.filters.ccs2coro import ccs2coroxml

from clufter.formats.ccs import ccs, ccsflat
from clufter.formats.coro import coroxml
from clufter.formats.pcs import pcs

from clufter.utils import apply_preserving_depth, \
                          apply_aggregation_preserving_depth, \
                          head_tail


class ChainResolve(unittest.TestCase):
    def testShapeMatch(self):

        filters = dict(
            ccs2ccsflat=ccs2ccsflat(ccs, ccsflat),
            ccsflat2pcs=ccsflat2pcs(ccsflat, pcs),
            ccs2coroxml=ccs2coroxml(ccs, coroxml),
        )

        @Command.deco('ccs2ccsflat', ('ccsflat2pcs', 'ccs2coroxml'))
        def cmd_chain_match(input='.in', output='.out', coro='.coro'):
            return ('file', input), (('file', output), ('file', coro))
        @Command.deco('ccs2ccsflat')
        def cmd_chain_nonmatch_01(input='.in', output='.out', coro='.coro'):
            return ('file', input), (('file', output), ('file', coro))
        @Command.deco('ccs2ccsflat',
                      ('ccsflat2pcs', 'ccs2coroxml', 'ccs2coroxml'))
        def cmd_chain_nonmatch_02(input='.in', output='.out', coro='.coro'):
            return ('file', input), (('file', output), ('file', coro))

        cmd_classes = (cmd_chain_match, cmd_chain_nonmatch_01,
                                        cmd_chain_nonmatch_02)
        cmd_names = map(lambda x: x.name, cmd_classes)
        commands = {}
        for cmd_cls, cmd_name in zip(cmd_classes, cmd_names):
            res_input = cmd_cls.filter_chain
            res_output = apply_preserving_depth(filters.get)(res_input)
            if apply_aggregation_preserving_depth(all)(res_output):
                #log.debug("resolve at `{0}' command: `{1}' -> {2}"
                #        .format(cmd_name, repr(res_input), repr(res_output)))
                commands[cmd_name] = cmd_cls(*res_output)
                continue
        match, nonmatches = head_tail(cmd_names)
        try:
            commands[match]({}, [])
        except Exception as e:
            print "{0}: {1}".format(match, e)
            self.assertTrue(False)
        else:
            self.assertTrue(True)
        for nonmatch in nonmatches:
            try:
                commands[nonmatch]({}, [])
            except CommandError as e:
                print "{0}: {1}".format(nonmatch, e)
                self.assertTrue(True)
            else:
                self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
