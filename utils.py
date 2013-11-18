# -*- coding: UTF-8 -*-
# Copyright 2012 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

import os


# name the exitcodes
ecodes = 'SUCCESS', 'FAILURE'
EC = type('EC', (), {n: v for v, n in enumerate('EXIT_' + i for i in ecodes)})


head_tail = lambda x=None, *y: (x, x if x is None else y)
filtervars = lambda src,which: {x: src[x] for x in which if x in src}
filtervarsdef = lambda src,which: {x: src[x] for x in which if src.get(x, None)}
filtervarspop = lambda src,which: {x: src.pop(x) for x in which if x in src}


def which(name, *where):
    where = tuple(os.path.abspath(i) for i in where)
    if 'PATH' in os.environ:
        path = tuple(i for i in os.environ['PATH'].split(os.pathsep)
                     if len(i.strip()))
    else:
        path = ()
    for p in where + path:
        check = os.path.join(p, name)
        if os.path.exists(check):
            return check
    else:
        return None


class ClufterError(Exception):
    def __init__(self, ctx_self, msg, *args):
        self.ctx_self = ctx_self
        self.msg = msg

    def __str__(self):
        ret = getattr(self.ctx_self, '__name__',
                      self.ctx_self.__class__.__name__)
        return ret + ': ' + self.msg.format(*self.args)


class ClufterPlainError(ClufterError):
    def __init__(self, msg, *args):
        super(ClufterPlainError, self).__init__(self, None, msg, *args)


# Inspired by http://stackoverflow.com/a/1383402
class classproperty(property):
    def __init__(self, fnc):
        property.__init__(self, classmethod(fnc))

    def __get__(self, this, owner):
        return self.fget.__get__(None, owner)()


class hybridproperty(property):
    def __init__(self, fnc):
        property.__init__(self, classmethod(fnc))

    def __get__(self, this, owner):
        return self.fget.__get__(None, this if this else owner)()
