# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from logging import getLogger

from .error import ClufterError
from .filter import filters
from .format_manager import FormatManager
from .plugin_registry import PluginManager
from .utils_2to3 import iter_values

log = getLogger(__name__)


class FilterManagerError(ClufterError):
    pass


class FilterManager(PluginManager):
    """Class responsible to manage filters and filtering itself"""
    _default_registry = filters

    @classmethod
    def _init_plugins(cls, filters, fmt_mgr=None, **kwargs):
        log.debug("Filters before resolving: {0}".format(filters))
        if fmt_mgr is None:
            fmts = set()
            for flt in iter_values(filters):
                # XXX composite format
                for attr in ('in_format', 'out_format'):
                    fmts.add(getattr(flt, attr))
            fmt_mgr = FormatManager.init_lookup(fmts, **kwargs)
        return cls._resolve(fmt_mgr.formats, filters)

    @staticmethod
    def _resolve(formats, filters):
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
