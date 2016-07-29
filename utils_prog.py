# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Program-specific commons"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from collections import Mapping, MutableMapping, MutableSequence, MutableSet
from optparse import Option
from os import environ, fdopen, isatty, pathsep
from os.path import abspath, dirname, samefile, \
                    isabs as path_isabs, \
                    isfile as path_isfile, \
                    join as path_join
from re import compile as re_compile
from subprocess import Popen
from sys import stderr, stdin, stdout

from . import package_name
from .error import ClufterError
from .utils import areinstances, \
                   filterdict_pop, \
                   func_defaults_varnames, \
                   isinstanceexcept, \
                   selfaware, \
                   tuplist

log = logging.getLogger(__name__)


#
# generics
#

mutables = (MutableMapping, MutableSequence, MutableSet)

class TweakedDict(MutableMapping):
    """Object representing command context"""

    class notaint_context(object):
        def __init__(self, self_outer, exit_off):
            self._exit_off = exit_off
            self._self_outer = self_outer
        def __enter__(self):
            self._exit_off |= not self._self_outer._notaint
            self._self_outer._notaint = True
        def __exit__(self, *exc):
            self._self_outer._notaint = not self._exit_off

    def __init__(self, initial=None, bypass=False, notaint=False):
        self._parent = self
        self._notaint = True
        if areinstances(initial, self):
            assert initial._parent is initial
            self._dict = initial._dict  # trust dict to have expected props
            notaint = initial._notaint
        else:
            self._dict = {}
            if initial is not None:
                if not isinstance(initial, Mapping):
                    initial = dict(initial)
                elif not isinstance(initial, MutableMapping):
                    # silently? follow the immutability
                    notaint = True
                    bypass = True
                if bypass or notaint:
                    self._dict = initial
                if not bypass:
                    # full examination
                    self._notaint = False  # temporarily need to to allow
                    map(lambda (k, v): self.__setitem__(k, v),
                                       initial.iteritems())
        self._notaint = notaint

    def __delitem__(self, key):
        if any(getattr(p, '_notaint', False) for p in self.anabasis):
            raise RuntimeError("Cannot del item in notaint context")
        del self._dict[key]

    def __getitem__(self, key):
        # any notainting parent incl. self is an authority for us
        try:
            ret = self._dict[key]
        except KeyError:
            if self._parent is self:
                raise
            ret = self._parent[key]
        if (isinstanceexcept(ret, mutables, TweakedDict)
            and any(getattr(p, '_notaint', False) for p in self.anabasis)):
            ret = type(ret)(ret)
        return ret

    @property
    def anabasis(self):
        """Traverse nested contexts hierarchy upwards"""
        return (self, )

    def setdefault(self, key, *args, **kwargs):
        """Allows implicit arrangements to be bypassed via `bypass` flag"""
        assert len(args) < 2
        bypass = kwargs.get('bypass', False)
        if bypass:  # for when adding MutableMapping that should be untouched
            return self._dict.setdefault(key, *args)
        try:
            return self.__getitem__(key)
        except KeyError:
            if not args:
                raise
            self.__setitem__(key, *args)
            return args[0]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return "<{0}: {1}>".format(repr(self.__class__), repr(self._dict))

    def __setitem__(self, key, value):
        # XXX value could be also any valid dict constructor argument
        if any(getattr(p, '_notaint', False) for p in self.anabasis):
            raise RuntimeError("Cannot set item in notaint context")
        self._dict[key] = value

    def prevented_taint(self, exit_off=False):
        """Context manager to safely yield underlying dicts while applied"""
        return self.notaint_context(self, exit_off)

ProtectedDict = lambda track: TweakedDict(track, notaint=True, bypass=True)


#
# command-line options related
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
        (lambda lo:
            lo[0] + ''.join(sorted(lo[1:],
                                   key=lambda x: int(x.lower() in 'aeiouy')))
        )(filter(lambda c: c.isalpha(), longopt))

class ExpertOption(Option):
    pass

make_option = \
    lambda *a, **kw: \
        (ExpertOption if kw.pop('expert', False) else Option)(*a, **kw)

# extrapolate make_option to specifically-encoded "plural"
make_options = lambda opt_decl: [make_option(*a, **kw) for a, kw in opt_decl]


def set_logging(opts):
    """Apply logging options as per `opts' to the live logging configuration"""
    rootlog = logging.getLogger()
    last_hdlr = rootlog.handlers.pop()
    if isinstance(last_hdlr, logging.FileHandler if opts.logfile
                             else logging.StreamHandler) \
      and (samefile(opts.logfile, last_hdlr.baseFilename)
           if opts.logfile else last_hdlr.stream is stderr):
        hdlr = last_hdlr
    else:
        hdlr = logging.FileHandler(opts.logfile) if opts.logfile \
               else logging.StreamHandler()
        hdlr.setFormatter(last_hdlr.formatter)
    rootlog.addHandler(hdlr)
    rootlog.setLevel(logging.getLevelName(opts.loglevel))


def PopenLog(cmd, *args, **kwargs):
    log.debug("Running: {0}".format(' '.join(cmd)))
    return Popen(cmd, *args, **kwargs)


class OneoffWrappedStdinPopen(object):
    """Singleton to watch for atmost one use of stdin in Popen context"""
    def __init__(self):
        self._used = False

    def __call__(self, args, **kwargs):
        if not 'stdin' in kwargs and '-' in args:
            if self._used:
                raise ClufterError(self, 'repeated use detected')
            kwargs['stdin'] = stdin
            # only the first '-' substituted
            args[args.index('-')] = '/dev/stdin'
            self._used |= True
        return PopenLog(args, **kwargs)

OneoffWrappedStdinPopen = OneoffWrappedStdinPopen()


#
# misc
#

# NB: distutils.spawn.find_executable
def which(name, single='', *paths, **redefine_check):
    """Mimic `which' UNIX utility

    Both `single` and `paths` denotes paths to be tried for `name` lookup,
    which includes a decision from the perspective of a filter function given
    by `check` keyword argument (default: a test if the file exists at all).

    What is special about `single` is that it can be defined as either
    plain one-path string, PATH-like-separated list of paths, or
    an iterable.  It is decomposed into a list of paths and then
    `paths` items appended.

    Apparently, when `name` is provided as an absolute path, only
    the `check` (i.e., no lookup) phase is performed.

    If nothing matching the criteria is found, `None` is returned,
    nominal path as per `name` (and `check` for that matter) otherwise.

    Empty string instructs code to use environment's PATH instead.
    """
    check, expand_path = redefine_check.pop('check', path_isfile), True
    if path_isabs(name):
        where, expand_path = [''], False
    else:
        where = list(single.split(pathsep) if not tuplist(single) else single)
        where.extend(paths)
        where.reverse()
    while where:
        p = where.pop()
        if not p:
            if expand_path:
                where.extend(reversed(environ.get('PATH', '').split(pathsep)))
                expand_path = False
                continue
            elif where:
                break  # degenerated case: multiple ''
        p = path_join(abspath(p), name)
        if check(p):
            return p
    else:
        return None


dirname_x = lambda p, c=1: reduce(lambda x, y: dirname(x), xrange(c), p)


@selfaware
def defer_common(me, fnc, skip=0):
    """Use when you have a func with common initial kwargs consumption

    Calling this on another function will, upon invocation, first look
    at default argument to `_common` keyword parameter, and if present,
    will consider it as a function to be run before the one passed as
    an argument; aside from returning a function decorated in a stated
    way, it will also return dict of function paramater defaults (joint
    for both original and '_common' function) and a list of joint
    function arguments.

    In other words, it allows DRY principle for common shared initial
    kwargs "consumer" function on top of (actually prior to) the function
    being passed in as an argument.
    """
    fnc_defaults, fnc_varnames = func_defaults_varnames(fnc, skip=skip)
    common = fnc_defaults.pop('_common', None)
    if not common:
        wrapfnc = fnc
    else:
        common_defaults, common_varnames, common = me(common, skip=skip)
        fnc_defaults.update(common_defaults)
        fnc_varnames = list(fnc_varnames)
        fnc_varnames.remove('_common')  # but we could rely on last argument
        fnc_varnames = tuple(fnc_varnames) + common_varnames

        def wrapfnc(cmd_ctxt, **kwargs):
            common(cmd_ctxt, **filterdict_pop(kwargs, *common_varnames))
            kwargs.pop('_common', None)
            return fnc(cmd_ctxt, **kwargs)
        wrapfnc.__doc__ = fnc.__doc__ + common.__doc__
    return fnc_defaults, fnc_varnames, wrapfnc


def getenv_namespaced(varname, value=None, namespace=package_name().upper()):
    """Obtain value of environment variable prefixed with `namespace + '_'`"""
    return environ.get('_'.join((namespace, varname)), value)


def setenv_namespaced(varname, value=None, namespace=package_name().upper()):
    """Set value of environment variable prefixed with `namespace + '_'`"""
    environ['_'.join((namespace, varname))] = value


# cf. https://github.com/karelzak/util-linux/blob/master/lib/colors.c#L107
#     https://github.com/karelzak/util-linux/blob/master/include/colors.h#L14
class FancyOutput(object):
    """
    Mean to produce more fancy output based on a simple tagging

    One can tag particular disjoint parts of the message like this:

        This is |error:error| and this is |warning:warning|.

    which produces

        This is error and this is warning.

    but on a terminal, both annotated words will be colorized as specified.
    Currently, it is hard-coded with a possibility for overrides through `cfg`
    collective keyword argument;  in the future terminal-colors.d scheme
    as introduced by util-linux package, see TERMINAL_COLORS.D(5),
    will be leveraged.

    Usage is simple, instantiate an object of this class, then pass it
    around your code and call it with a message to be produced (possibly
    using the introduced tagging) as a parameter.

    Other per-message-emit, keyword, parameters:
        base    additionally wrap the whole message with this default markup
                (only markup is taken into account as such)
        urgent  produce the message regardless of `quiet` parameter
                in the constructor
    """
    logic_colors = (
        'error',
        'header',
        'highlight',
        'note',
        'subheader',
        'warning',

        'pcscmd_comment',
        'pcscmd_file',
        'pcscmd_pcs',
    )
    re_color = re_compile(
        '\|(?P<logic>' + '|'.join(logic_colors) + '):(?P<msg>[^\|]*)\|'
    )

    colors = dict(
        black        = "\033[30m",
        blue         = "\033[34m",
        brown        = "\033[33m",
        cyan         = "\033[36m",
        darkgray     = "\033[1;30m",
        gray         = "\033[37m",
        green        = "\033[32m",
        lightblue    = "\033[1;34m",
        lightcyan    = "\033[1;36m",
        lightgray    = "\033[37m",
        lightgreen   = "\033[1;32m",
        lightmagenta = "\033[1;35m",
        lightred     = "\033[1;31m",
        magenta      = "\033[35m",
        red          = "\033[31m",
        yellow       = "\033[1;33m",

        restore      = '\033[0m',
    )

    table = dict(
        error     = 'lightred',
        header    = 'magenta',
        highlight = 'green',
        note      = 'brown',
        subheader = 'blue',
        warning   = 'red',

        pcscmd_comment = 'brown',
        pcscmd_file    = 'magenta',
        pcscmd_pcs     = 'blue',
    )

    @classmethod
    def get_color(cls, spec):
        return cls.colors.get(spec, spec if spec.startswith('\033[') or not spec
                                    else '\033[' + spec)

    # TODO use /etc/terminal-colors.d/clufter.{enable,disable,scheme}
    def __init__(self, f=stdout, recheck=False, color=None, quiet=False,
                 prefix='', **cfg):
        if not isinstance(f, file):
            f = fdopen(f, "a")
        self._f = f
        self._quiet = quiet
        self._prefix = prefix
        self._table = self.table.copy().update(cfg)
        if color is not None:
            recheck = False
        else:
            color = isatty(f.fileno()) if hasattr(f, 'fileno') else False
        self._handle = self.handle_recheck if recheck else \
                       self.handle_color if color else self.handle_std

    def __call__(self, s, **kwargs):
        if self._quiet and not kwargs.pop('urgent', False):
            return
        if self._prefix:
            prefix = self._prefix
            if 'prefix_arg' in kwargs:
                prefix = prefix.format(kwargs['prefix_arg'])
            s = prefix + s
        self._handle(s, **kwargs)
        self._f.flush()

    def handle_recheck(self, s, **kwargs):
        (self.handle_color if isatty(self._f) else self.handle_std)(s, **kwargs)

    def handle_std(self, s, **kwargs):
        self._f.write(self.re_color.sub(lambda m: m.group('msg'), s) + '\n')

    def handle_color(self, s, base=None, **kwargs):
        end = self.colors['restore']
        flip = end + self.get_color(self.table.get(base, ''))
        self._f.write(
            flip
            + self.re_color.sub(
                lambda m:
                    end
                    + self.get_color(self.table.get(m.group('logic'), ''))
                    + m.group('msg')
                    + flip,
                s
            )
            + end
            + '\n'
        )


def docformat(*args, **kwargs):
    """Workaround unability to set __doc__ as an evaluated (subst) expression"""
    def deco(fnc):
        if hasattr(fnc, '__doc__'):
            try:
                fnc.__doc__ = fnc.__doc__.format(*args, **kwargs)
            except IndexError:
                pass
        return fnc
    return deco
