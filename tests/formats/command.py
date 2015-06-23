# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing format"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from unittest import TestCase

from .format_manager import FormatManager
command = FormatManager.init_lookup('command').formats['command']


class FormatsCommandTestCase(TestCase):
    def testBytestringToMerged(self):
        c = command('bytestring', 'cut -f 1 -d @ emails.txt')
        #print c('merged')
        self.assertEqual(c.MERGED(),
                         ['cut', '-f', '1', '-d', '@', 'emails.txt'])

    def testMergedToBytestring(self):
        c = command('merged', ['cut', '-f', '1', '-d', '@', 'emails.txt'])
        #print c('bytestring')
        self.assertEqual(c.BYTESTRING(), 'cut -f 1 -d @ emails.txt')

    def testBytestringToSeparated(self):
        c = command('bytestring', 'cut -f 1 -d @ emails.txt')
        #print c('separated')
        self.assertEqual(c.SEPARATED(),
                         [('cut',), ('-f', '1'), ('-d', '@'), ('emails.txt', )])

    def testSeparatedToBytestring(self):
        c = command('separated',
                    [('cut',), ('-f', '1'), ('-d', '@'), ('emails.txt', )])
        #print c('bytestring')
        self.assertEqual(c.BYTESTRING(), 'cut -f 1 -d @ emails.txt')

    def testMergedToSeparated(self):
        c = command('merged', ['cut', '-f', '1', '-d', '@', 'emails.txt'])
        #print c('separated')
        self.assertEqual(c.SEPARATED(),
                         [('cut',), ('-f', '1'), ('-d', '@'), ('emails.txt', )])

    def testSeparatedToMerged(self):
        c = command('separated',
                    [('cut',), ('-f', '1'), ('-d', '@'), ('emails.txt', )])
        #print c('merged')
        self.assertEqual(c.MERGED(),
                         ['cut', '-f', '1', '-d', '@', 'emails.txt'])

    def testDictToMerged(self):
        c = command('dict', {'__cmd__': ('cut', ), '-f': ('1', ), '-d': ('@', ),
                             '__args__': ('emails.txt', )})
        #print c('merged')
        self.assertEqual(c.MERGED(),
                         ['cut', '-f', '1', '-d', '@', 'emails.txt'])


    def testMagicBytestringToDict(self):
        c = command('bytestring',
                    'gpg -k 60BCBB4F5CD7F9EF::~/.gnupg/pubring.gpg',
                    magic_split=True)
        #print c('merged')
        self.assertEqual(c.DICT(),
                         OrderedDict([('__cmd__', ['gpg']),
                                      ('-k', [('60BCBB4F5CD7F9EF',
                                               '~/.gnupg/pubring.gpg')])]))

    def testBytestringToMergedQuoted(self):
        c = command('bytestring', 'cut -f 1 -d @ "my private emails.txt"')
        #print c('merged')
        self.assertEqual(c.MERGED(),
                         ['cut', '-f', '1', '-d', '@', "'my private emails.txt'"])

from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
