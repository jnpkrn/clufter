# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
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
        if parent is None:
            parent = self
        self._parent = parent
        try:
            self._dict = dict(initial)
        except TypeError:
            self._dict = {}

    def __delitem__(self, key):
        del self._dict[key]

    def __getitem__(self, key):
        #return self._dict[key]
        return self._dict.get(key)  # make it soft-error (->setdefault reimpl.)

    def setdefault(self, key, default=None):
        return self._dict.setdefault(key, default)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __setitem__(self, key, value):
        self._dict[key] = CommandContextBase(initial=value, parent=self) \
                          if isinstance(value, dict) else value

    @property
    def parent(self):
        return self._parent


class CommandContext(CommandContextBase):
    def __init__(self, *args, **kwargs):
        super(CommandContext, self).__init__(*args, **kwargs)
        self._filters = {}

    def _wrapping_nested_context(self, obj):
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
                            lambda this, *args, **kwargs: \
                                ret(this, this, *args, **kwargs)
                else:
                    try:
                        ret = super(wrapped, self).__getattribute__(name)
                    except AttributeError:
                        ret = obj.__getattribute__(name)
                return ret

            def __setattribute__(self, name, value):
                obj.__setattribute__(name, value)
        return (wrapped(parent=self))

    def ensure_filter(self, flt):
        existing, key = self._filters, flt.__class__.name
        ret = existing.get(key, None)
        if ret:
            assert id(ret.ctxt_wrapped) == id(flt)
        else:
            ret = existing[key] = self._wrapping_nested_context(flt)
        return ret

    def ensure_filters(self, flts):
        return map(self.ensure_filter, flts)

    def filter(self, which):
        return self._filters[which]
