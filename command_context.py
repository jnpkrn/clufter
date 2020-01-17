# -*- coding: UTF-8 -*-
# Copyright 2020 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command context, i.e., state distributed along filters chain"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping
from logging import getLogger

from .error import ClufterError
from .utils import isinstanceexcept
from .utils_prog import TweakedDict

log = getLogger(__name__)


class CommandContextError(ClufterError):
    pass


class CommandContextBase(TweakedDict):
    """Object representing command context"""
    def __init__(self, initial=None, parent=None, **kwargs):
        super(CommandContextBase, self).__init__(initial=initial, **kwargs)
        if parent is not None:
            self._parent = parent

    @property
    def anabasis(self):
        """Traverse nested contexts hierarchy upwards"""
        cur = self
        while True:
            yield cur
            if cur is cur._parent:
                break
            cur = cur._parent

    @property
    def parent(self):
        return self._parent

    def __setitem__(self, key, value):
        # XXX value could be also any valid dict constructor argument
        if any(getattr(p, '_notaint', False) for p in self.anabasis):
            raise RuntimeError("Cannot set item in notaint context")
        self._dict[key] = CommandContextBase(initial=value, parent=self) \
                          if isinstanceexcept(value, MutableMapping,
                                                     CommandContextBase) \
                          else value


class CommandContext(CommandContextBase):
    class notaint_context(CommandContextBase.notaint_context):
        def __init__(self, self_outer, exit_off):
            super(self.__class__, self).__init__(self_outer, exit_off)
            self._fc = self_outer['__filter_context__'] \
                       .prevented_taint(exit_off)
        def __enter__(self):
            super(self.__class__, self).__enter__()
            self._fc.__enter__()
        def __exit__(self, *exc):
            self._fc.__exit__()
            super(self.__class__, self).__exit__()

    def __init__(self, *args, **kwargs):
        # filter_context ... where global arguments for filters to be stored
        # filters        ... where filter instance + arguments hybrid is stored
        super(CommandContext, self).__init__(*args, **kwargs)
        # could be cycle up to self if not bypassed
        self['__filter_context__'] = {}  # here we actually want a fallback
        self['__filters__'] = CommandContextBase()

    @staticmethod
    def _wrapping_nested_context(obj):
        class wrapped(CommandContextBase):
            def __getattribute__(self, name):
                if name == 'ctxt_wrapped':
                    ret = obj
                elif name == 'ctxt_set':
                    ret = lambda self, **kwargs: self.update(kwargs)
                elif name.startswith('ctxt_'):
                    # by convention, ctxt_* methods are using second
                    # argument to pass the respective (nested) context
                    ret = obj.__getattribute__(name)
                    if callable(ret):
                        ret = \
                            lambda *args, **kwargs: \
                                obj.__getattribute__(name)(self, *args, **kwargs)
                else:
                    try:
                        if name.startswith('_'):
                            raise KeyError  # dot=index access not for internals
                        ret = self.__getitem__(name)
                    except KeyError:
                        try:
                            ret = super(wrapped, self).__getattribute__(name)
                        except AttributeError:
                            ret = obj.__getattribute__(name)
                return ret

            def __setattribute__(self, name, value):
                obj.__setattribute__(name, value)
        return wrapped

    def ensure_filter(self, flt):
        existing, key = self['__filters__'], flt.__class__.name
        ret = existing.get(key, None)
        if ret is not None:
            assert id(ret.ctxt_wrapped) == id(flt)
        else:
            ret = self._wrapping_nested_context(flt)
            ret = existing[key] = ret(parent=self['__filter_context__'])
        return ret

    def ensure_filters(self, flts):
        return tuple(self.ensure_filter(f) for f in flts)

    def filter(self, which=None):
        if which is not None:
            ret = self['__filters__'][which]
        else:
            ret = self['__filter_context__']
        return ret
