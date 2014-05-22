# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command context, i.e., state distributed along filters chain"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from collections import MutableMapping
import logging

from .error import ClufterError

log = logging.getLogger(__name__)


class CommandContextError(ClufterError):
    pass


class CommandContextBase(MutableMapping):
    """Object representing command context"""
    def __init__(self, initial=None, parent=None):
        try:
            self._dict = initial if type(initial) is dict else dict(initial)
        except TypeError:
            self._dict = {}
        self._parent = parent if parent is not None else self

    def __delitem__(self, key):
        del self._dict[key]

    def __getitem__(self, key):
        try:
            return self._dict[key]
        except KeyError:
            pass
        # make it soft-error (->setdefault reimpl.)
        return None if self._parent is self else self._parent[key]

    def setdefault(self, key, default=None):
        return self._dict.setdefault(key, default)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __setitem__(self, key, value):
        # XXX value could be also any valid dict constructor argument
        self._dict[key] = CommandContextBase(initial=value, parent=self) \
                          if isinstance(value, dict) else value

    @property
    def parent(self):
        return self._parent


class CommandContext(CommandContextBase):
    def __init__(self, *args, **kwargs):
        # filter_context ... where global arguments for filters to be stored
        # filters        ... where filter instance + arguments hybrid is stored
        super(CommandContext, self).__init__(*args, **kwargs)
        # could be cycle up to self if {} was used instead
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
