# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from _shared import empty_opts

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from unittest import TestCase
from os.path import dirname, join
from os import remove, stat

from .command import Command, CommandError
from .filter_manager import FilterManager

from .format import formats
formats = formats.plugins


class ChainResolve(TestCase):
    def testShapeAndProtocolMatch(self):
        filters = FilterManager.init_lookup('ccs2ccsflat',
                                            'ccsflat2cibprelude',
                                            'ccs2needlexml',
                                            'cmd-annonate',
                                            'stringiter-combine3',
                                            'cmd-wrap',
                                            'ccs-propagate-cman',
                                            'needlexml2pcscmd',
                                            'needleqdevicexml2pcscmd',
                                            ext_plugins=False).plugins
        from tempfile import mktemp
        testfile = join(dirname(__file__), 'empty.conf')
        testoutput = mktemp(prefix='out', suffix='.conf',
                            dir=join(dirname(__file__), 'tmp'))

        @Command.deco(('ccs2ccsflat',
                          ('ccsflat2cibprelude'),
                          ('ccs2needlexml')))
        def cmd_chain_match_01(cmd_ctxt,
                               input=testfile,
                               output=testoutput,
                               coro='.coro'):
            return (
                ('file', input),
                (
                    ('file', output),
                    ('file', coro),
                ),
            )
        @Command.deco(('ccs2ccsflat'))
        def cmd_chain_match_02(cmd_ctxt,
                               input=testfile,
                               output=testoutput,
                               coro='.coro'):
            return (
                ('file', input),
                ('file', output),
            )
        @Command.deco(('cmd-annotate',
                                      ('stringiter-combine3',
                                          ('cmd-wrap'))),
                      ('ccs2ccsflat',
                          ('ccs-propagate-cman',
                              ('ccs2needlexml',
                                  ('needlexml2pcscmd',
                                      ('stringiter-combine3'  # , ('cmd-wrap' ...
                                       )),
                                  ('needleqdevicexml2pcscmd',
                                      ('stringiter-combine3'  # , ('cmd-wrap' ...
                                       ))))))
        def cmd_chain_match_03(cmd_ctxt,
                               input=testfile,
                               output=testoutput):
            cmd_ctxt['pcscmd_force'] = cmd_ctxt['pcscmd_verbose'] = False
            cmd_ctxt['pcscmd_dryrun'] = cmd_ctxt['pcscmd_enable'] = False
            cmd_ctxt['pcscmd_noauth'] = cmd_ctxt['pcscmd_noguidance'] = True
            cmd_ctxt['pcscmd_start_wait'] = 60
            return (
                (
                    ('void',),
                    (
                                                        (
                                                            ('file', output),
                                                        ),
                    ),
                ), (
                    ('file', input),
                    #(
                    #    (
                    #        (
                    #                                (
                    #                                    (
                    #                                        ('file', output),
                    #                                    ),
                    #                                ),
                    #            # already tracked
                    #            #                    (
                    #            #                        (
                    #            #                            ('file', output),
                    #            #                        ),
                    #            #                    ),
                    #        ),
                    #    ),
                    #),
                ),
            )
        # [filter resolution #1 of output:
        # `('file', 'tests/tmp/outTbmuFs.conf')' protocol not suitable]
        @Command.deco(('ccs2ccsflat'))
        def cmd_chain_nonmatch_01(cmd_ctxt,
                                  input=testfile,
                                  output=testoutput,
                                  coro='.coro'):
            return (
                ('file', input),
                (
                    ('file', output),
                    ('file', coro),
                )
            )
        # [filter `ccs2needlexml' is feeded by `ccsflat2cibprelude' more than
        # once]
        @Command.deco(('ccs2ccsflat',
                          ('ccsflat2cibprelude'),
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
                    ('file', coro),
                )
            )
        # malformed protocol name
        # [filter resolution #2 of output: `life' protocol not suitable]
        @Command.deco(('ccs2ccsflat',
                          ('ccsflat2cibprelude'),
                          ('ccs2needlexml')))
        def cmd_chain_nonmatch_03(cmd_ctxt,
                                  input=testfile,
                                  output=testoutput,
                                  coro='.coro'):
            return (
                ('file', input),
                (
                    ('file', output),
                    ('life', coro),
                )
            )
        cmd_classes = (
            cmd_chain_match_01,
            cmd_chain_match_02,
            cmd_chain_match_03,
            cmd_chain_nonmatch_01,
            cmd_chain_nonmatch_02,
            cmd_chain_nonmatch_03
        )
        split = cmd_classes.index(cmd_chain_nonmatch_01)
        for i, cmd_cls in enumerate(cmd_classes):
            try:
                ret = cmd_cls(filters)(empty_opts, ())  # no opts/args
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


from os.path import join, dirname as d; execfile(join(d(__file__), '_gone'))
