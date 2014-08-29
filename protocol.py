# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base protocol stuff (metaclass, etc.)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .plugin_registry import PluginRegistry
from .utils import tuplist
from .utils_prog import cli_undecor

log = logging.getLogger(__name__)


class protocols(PluginRegistry):
    """Protocol registry (to be used as a metaclass for filters)

    To be noted, this harness is solely optional, and only good to allow
    early discovery of the typos in the protocols and to maintain some
    in-code documentation of their usage as opposed to much further
    in the processing with some files already successfully produced, etc.
    """
    @classmethod
    def register(registry, pr):
        # undecor to pass the checks in probe
        return registry.probe(cli_undecor(pr),
                              pr if isinstance(pr, Protocol) else Protocol(pr))


class Protocol(str):
    """Class intended to be (exceptionally) instantioned (enhanced string)"""
    __metaclass__ = protocols

    def __new__(cls, *args, **kwargs):
        ret = super(Protocol, cls).__new__(cls, *args, **kwargs)
        return protocols.register(ret)

    def ensure_proto(self, value):
        return value if tuplist(value) else (self, value)
