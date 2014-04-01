# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Filter manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .error import ClufterError
from .filter import filters
from .format import CompositeFormat
from .plugin_registry import PluginManager
from .utils import tuplist
from .utils_func import apply_preserving_depth, \
                        apply_aggregation_preserving_depth, \
                        apply_intercalate

log = logging.getLogger(__name__)


class FilterManagerError(ClufterError):
    pass


class FilterManager(PluginManager):
    """Class responsible to manage filters and filtering itself"""
    _default_registry = filters

    def _init_handle_plugins(self, filters, fmt_mgr):
        log.debug("Filters before resolving: {0}"
                  .format(filters))
        self._filters = self._resolve(fmt_mgr.formats, filters)

    @staticmethod
    def _resolve(formats, filters):
        def get_composite_onthefly(formats):
            composite_onthefly = \
                lambda protocol, *args: \
                    CompositeFormat(protocol, formats=formats, *args)
            # XXX currently instantiation only (no match for composite classes)
            composite_onthefly.as_instance = composite_onthefly
            return composite_onthefly

        for flt_name, flt_cls in filters.items():
            res_input = [flt_cls.in_format, flt_cls.out_format]
            res_output = apply_preserving_depth(formats.get)(res_input)
            if apply_aggregation_preserving_depth(all)(res_output):
                log.debug("Resolve at `{0}' filter: `{1}' -> {2}"
                          .format(flt_name, repr(res_input), repr(res_output)))
                # capture composite formats if present;  when running
                # into composite format, we replace in-situ the whole iterable
                # with as-of-now resolved formats with lazily pulled
                # CompositeFormat passing it these formats along the standard
                # business (as opposed to on-the-fly class creation when it
                # probably won't be ever instantiated anyway);
                # extra lambda wrapping so as to surely make a closure around
                # ("remember correctly") the current value of res_output
                res_output = tuple(
                    get_composite_onthefly(o) if tuplist(o) else o
                    for o in res_output
                )
                filters[flt_name] = flt_cls(*res_output)
                continue
            # drop the filter if cannot resolve any of the formats
            res_input = apply_intercalate(res_input)
            map(lambda (i, x): log.warning("Resolve at `{0}' filter:"
                                           " `{1}' (#{2}) format fail"
                                           .format(flt_name, res_input[i], i)),
                filter(lambda (i, x): not(x),
                       enumerate(apply_intercalate(res_output))))
            filters.pop(flt_name)
        return filters

    @property
    def filters(self):
        return self._filters.copy()

    def __call__(self, which, in_decl, **kwargs):
        flt = self._filters[which]
        in_obj = flt.in_format.as_instance(*in_decl)
        return flt(in_obj, **kwargs)
