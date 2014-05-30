# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Various little+independent helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


# inspired by http://stackoverflow.com/a/4374075
mutable = lambda x: isinstance(x, (basestring, int, long, bool, float, tuple))

tuplist = lambda x: isinstance(x, (tuple, list))
# turn args into tuple unless single tuplist arg
args2sgpl = \
    lambda x=(), *y: x if not y and tuplist(x) else (x, ) + y
args2combsgpl = arg2wrapped = \
    lambda x=(), *y: x if not y and tuplist(x) and len(x) > 1 else (x, ) + y
args2unwrapped = \
    lambda x=None, *y: x if not y else (x, ) + y
# turn args into tuple unconditionally
args2tuple = lambda *args: tuple(args)
any2iter = \
    lambda x: \
        x if hasattr(x, 'next') and hasattr(x.next, '__call__') \
        else iter(args2sgpl(x, None))

head_tail = \
    lambda x=None, *y, **kwargs: \
        (x, args2sgpl(*y)) if not tuplist(x) or kwargs.get('stop', 0) \
                           else (head_tail(stop=1, *tuple(x) + y))

filtervars = \
    lambda src, which: dict((x, src[x]) for x in which if x in src)
filtervarsdef = \
    lambda src, which: dict((x, src[x]) for x in which if src.get(x, None))
filtervarspop = \
    lambda src, which: dict((x, src.pop(x)) for x in which if x in src)


#
# function introspection related
#

def func_defaults_varnames(func, skip=0, fix_generator_tail=True):
    """Using introspection, get arg defaults (dict) + all arg names (tuple)

    Parameters:
        skip                how many initial arguments to skip
        fix_generator_tail  see http://stackoverflow.com/questions/9631777
                            https://mail.python.org/pipermail/python-list/
                                    2013-November/661304.html
    """
    func_varnames = func.func_code.co_varnames
    assert len(func_varnames) - skip >= len(func.func_defaults)

    # look at tail possibly spoiled with implicit generator's stuff ala "_[1]"
    fix = 0
    for i in xrange(len(func_varnames) if fix_generator_tail else 0, skip, -1):
        if func_varnames[i - 1][0] not in "_.":
            break
        fix -= 1

    func_varnames = func_varnames[skip:fix or None]
    func_defaults = dict(zip(
        func_varnames,
        func.func_defaults[-len(func_varnames):]  # "fix" auto-accommodated
    ))

    return func_defaults, func_varnames


#
# decorators
#

def selfaware(func):
    """Decorator suitable for recursive staticmethod"""
    def selfaware_inner(*args, **kwargs):
        return func(selfaware(func), *args, **kwargs)
    map(lambda a: setattr(selfaware_inner, a, getattr(func, a)),
        ('__doc__', '__name__'))
    return selfaware_inner


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
