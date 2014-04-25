# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Various helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import os
import sys
from optparse import make_option
from subprocess import Popen

from .error import ClufterError


def selfaware(func):
    """Decorator suitable for recursive staticmethod"""
    def selfaware_inner(*args, **kwargs):
        return func(selfaware(func), *args, **kwargs)
    map(lambda a: setattr(selfaware_inner, a, getattr(func, a)),
        ('__doc__', '__name__'))
    return selfaware_inner

# inspired by http://stackoverflow.com/a/4374075
mutable = lambda x: isinstance(x, (basestring, int, long, bool, float, tuple))

tuplist = lambda x: isinstance(x, (tuple, list))
# turn args into tuple unless single tuplist arg
args2sgpl = \
    lambda x=(), *y: x if not y and tuplist(x) else (x, ) + y
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


def which(name, *where):
    """Mimic `which' UNIX utility"""
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


#
# command-line options and function introspection related
#

# dashes recommended by 5 of 4 terminal fanboys
# NB underscores -> dashes swap is idempotent in regards to the member
#    name of where optparse stores respective option value, but here
#    the list of possible operations to preserve such property stops!
#    + also to preserve reversibility/bijection, original ought to be
#      free of the substituting character
cli_decor = lambda x: x.replace('_', '-')
cli_undecor = lambda x: x.replace('-', '_')

# prioritize consonants, deprioritize vowels (except for the first letter
# overall), which seems to be widely adopted technique for selecting short
# options based on their long counterparts ;)
# XXX could eventually also resort to using upper-case chars
longopt_letters_reprio = \
    lambda longopt: \
        (lambda lo: \
            lo[0] + ''.join(sorted(lo[1:],
                                   key=lambda x: int(x.lower() in 'aeiouy')))
        )(filter(lambda c: c.isalpha(), longopt))

# extrapolate optparse.make_option to specifically-encoded "plural"
make_options = lambda opt_decl: [make_option(*a, **kw) for a, kw in opt_decl]

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


class OneoffWrappedStdinPopen(object):
    """Singleton to watch for atmost one use of stdin in Popen context"""
    def __init__(self):
        self._used = False

    def __call__(self, args, **kwargs):
        if not 'stdin' in kwargs and '-' in args:
            if self._used:
                raise ClufterError(self, 'repeated use detected')
            kwargs['stdin'] = sys.stdin
            # only the first '-' substituted
            args[args.index('-')] = '/dev/stdin'
            self._used |= True
        return Popen(args, **kwargs)

OneoffWrappedStdinPopen = OneoffWrappedStdinPopen()


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
