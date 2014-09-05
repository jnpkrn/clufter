# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .error import ClufterError
from .filter import filters
from .format import CompositeFormat
from .plugin_registry import PluginManager

log = logging.getLogger(__name__)


class FilterManagerError(ClufterError):
    pass


class FilterManager(PluginManager):
    """Class responsible to manage filters and filtering itself"""
    _default_registry = filters

    @classmethod
    def _init_plugins(cls, filters, fmt_mgr):
        log.debug("Filters before resolving: {0}".format(filters))
        return cls._resolve(fmt_mgr.formats, filters)

    @staticmethod
    def _resolve(formats, filters):
        def get_composite_onthefly(formats):
            # XXX should rather be implemented by CompositeFormat itself?
            composite_onthefly = \
                lambda protocol, *args: \
                    CompositeFormat(protocol, formats=formats, *args)
            # XXX currently instantiation only (no match for composite classes)
            composite_onthefly.as_instance = composite_onthefly
            composite_onthefly.context = CompositeFormat.context
            return composite_onthefly

        for flt_name, flt_cls in filters.items():
            ret = flt_cls(formats)
            if ret is not None:
                filters[flt_name] = ret
            else:
                filters.pop(flt_name)
        return filters

    @property
    def filters(self):
        return self._plugins

    def __call__(self, which, in_decl, **kwargs):
        flt = self._plugins[which]
        in_obj = flt.in_format.as_instance(*in_decl)
        return flt(in_obj, **kwargs)
