# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base exception classes and exit code definitions"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


# name the exitcodes
ecodes = 'SUCCESS', 'FAILURE'
EC = type('EC', (), dict((n, v) for v, n
                         in enumerate('EXIT_' + i for i in ecodes)))


class ClufterError(Exception):
    def __init__(self, ctx_self, msg, *args):
        self.ctx_self = ctx_self
        self.msg = msg
        self.args = args

    def __str__(self):
        ret = ''
        if self.ctx_self:
            ret = getattr(self.ctx_self, '__name__',
                          self.ctx_self.__class__.__name__)
            ret += ': '
        return ret + self.msg.format(*self.args)


class ClufterPlainError(ClufterError):
    def __init__(self, msg, *args):
        super(ClufterPlainError, self).__init__(None, msg, *args)
