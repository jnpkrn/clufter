# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base protocol stuff (metaclass, etc.)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from collections import MutableMapping
from logging import getLogger

from .plugin_registry import PluginRegistry
from .utils import args2sgpl, tuplist
from .utils_prog import cli_undecor

log = getLogger(__name__)

protodict = lambda x: isinstance(x, MutableMapping) and 'passin' in x
protodictval = lambda x: args2sgpl(x['passin']) if protodict(x) else x


class protocols(PluginRegistry):
    """Protocol registry (to be used as a metaclass for filters)

    To be noted, this harness is solely optional, and only good to allow
    early discovery of the typos in the protocols and to maintain some
    in-code documentation of their usage as opposed to much further
    in the processing with some files already successfully produced, etc.
    """
    _namespace = ''  # avoid the plugins module-import namespace, unused anyway

    @classmethod
    def register(registry, pr):
        # undecor to pass the checks in probe
        return registry.probe(cli_undecor(pr),
                              pr if isinstance(pr, Protocol) else Protocol(pr))


class Protocol(str):
    """Class intended to be (exceptionally) instantiated (enhanced string)"""
    __metaclass__ = protocols

    def __new__(cls, *args, **kwargs):
        ret = super(Protocol, cls).__new__(cls, *args, **kwargs)
        return protocols.register(ret)

    def ensure_proto(self, value=None):
        work_val = protodictval(value)
        work_val = work_val if tuplist(work_val) else (str(self), work_val) \
                            if work_val is not None else (str(self), )
        if protodict(value):
            value['passin'] = work_val
            work_val = value
        return work_val
