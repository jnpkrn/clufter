# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .filter import filters

log = logging.getLogger(__name__)


class FilterManager(object):
    """Class responsible to manage filters and filtering itself"""
    def __init__(self, fmt_mgr, registry=filters, paths=(), filters={}):
        self._registry = registry
        filters = dict(registry.discover(paths), **filters)
        log.debug("Filters before resolving: {0}"
                  .format(filters))
        self._filters = self._resolve(fmt_mgr.formats, filters)

    @staticmethod
    def _resolve(formats, filters):
        for flt_name, flt_cls in filters.items():
            in_format = formats.get(flt_cls.in_format)
            out_format = formats.get(flt_cls.out_format)
            if in_format is not None and out_format is not None:
                log.debug("Resolve at `{0}' filter: `{1}' -> {2},"
                          " `{3}' -> {4}"
                          .format(flt_name, flt_cls.in_format, in_format,
                                  flt_cls.out_format, out_format))
                filters[flt_name] = flt_cls(in_format, out_format)
                continue
            # drop the filter if cannot resolve either format
            if not in_format:
                log.warning("Resolve at `{0}' filter: `{1}' input format fail"
                            .format(flt_name, flt_cls.in_format))
            if not out_format:
                log.warning("Resolve at `{0}' filter: `{1}' output format fail"
                            .format(flt_name, flt_cls.out_format))
            filters.pop(flt_name)
        return filters

    @property
    def filters(self):
        return self._filters.copy()

    @property
    def registry(self):
        return self._registry

    def __call__(self, which, in_decl, **kwargs):
        flt = self._filters[which]
        in_obj = flt.in_format(*in_decl)
        return flt(in_obj, **kwargs)
