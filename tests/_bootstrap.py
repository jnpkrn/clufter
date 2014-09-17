# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Bootstrap the environment for testing"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from sys import modules, path
from os import getcwd
from os.path import basename, dirname, abspath


if __name__ != 'main_bootstrap':
    # XXX recognize when this file executed directly and report

    # if not run from main-bootstrap, verbose logging desired
    from os import environ
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(environ.get('LOGLEVEL') or logging.DEBUG)

# in interactive run, we have no __file__
__file__ = str(globals().get('__file__', ''))  # convert from possibly unicode
if __file__:
    # inject PYTHONPATH we are to use
    root = reduce(lambda x, y: dirname(x), xrange(2), abspath(__file__))
else:
    root = getcwd()
path.insert(0, dirname(root))

# set the correct __package__ for relative imports
__package__ = basename(root)
if __package__ not in modules:
    modules[__package__] = __import__(__package__)

# also normalize the __file__
__file__ = abspath(__file__)


# XXX previous attempt to get unittest.main executed automagically at the end,
#     which was failing likely because unittest uses Threading that register
#     another atexit handler somehow interfering w/ its main started from here
#if __name__ == '__main__':
#    def main()
#    from atexit import register
#    from unittest import main
#    register(main)
#    # hmm, see https://code.google.com/p/modwsgi/issues/detail?id=197
#    # https://github.com/GrahamDumpleton/mod_wsgi/commit/fdef274
#    register(lambda: __import__('dummy_threading'))
