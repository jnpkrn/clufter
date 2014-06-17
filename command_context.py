# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command context, i.e., state distributed along filters chain"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from collections import MutableMapping, MutableSequence, MutableSet
import logging

from .error import ClufterError
from .utils import isinstanceexcept

log = logging.getLogger(__name__)
mutables = (MutableMapping, MutableSequence, MutableSet)


class CommandContextError(ClufterError):
    pass


class CommandContextBase(MutableMapping):
    """Object representing command context"""
    def __init__(self, initial=None, parent=None, bypass=False):
        self._parent = parent if parent is not None else self
        if isinstance(initial, CommandContextBase):
            assert initial._parent is None
            self._dict = initial._dict  # trust dict to have expected props
        else:
            self._dict = {}
            if initial is not None:
                if not isinstance(initial, MutableMapping):
                    initial = dict(initial)
                map(lambda (k, v): self.setdefault(k, v, bypass=bypass),
                                   initial.iteritems())

    def __delitem__(self, key):
        del self._dict[key]

    def __getitem__(self, key):
        try:
            ret = self._dict[key]
        except KeyError:
            if self._parent is self:
                raise
            ret = self._parent[key]
        if isinstanceexcept(ret, mutables, CommandContextBase):
            ret = ret.copy()
        return ret

    def setdefault(self, key, *args, **kwargs):
        """Allows implicit arrangements to be bypassed via `bypass` flag"""
        assert len(args) < 2
        bypass = kwargs.get('bypass', False)
        if bypass:
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

    def __setitem__(self, key, value):
        # XXX value could be also any valid dict constructor argument
        self._dict[key] = CommandContextBase(initial=value, parent=self) \
                          if isinstanceexcept(value, MutableMapping,
                                                     CommandContextBase) \
                          else value

    @property
    def parent(self):
        return self._parent


class CommandContext(CommandContextBase):
    def __init__(self, *args, **kwargs):
        # filter_context ... where global arguments for filters to be stored
        # filters        ... where filter instance + arguments hybrid is stored
        super(CommandContext, self).__init__(*args, **kwargs)
        # could be cycle up to self if not bypassed
        self['__filter_context__'] = CommandContextBase()
        self['__filters__'] = CommandContextBase()

    @staticmethod
    def _wrapping_nested_context(obj):
        class wrapped(CommandContextBase):
            def __getattribute__(self, name):
                if name == 'ctxt_wrapped':
                    return obj
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
        return map(self.ensure_filter, flts)

    def filter(self, which=None):
        if which is not None:
            ret = self['__filters__'][which]
        else:
            ret = self['__filter_context__']
        return ret
