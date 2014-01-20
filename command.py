# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base command stuff (TBD)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .plugin_registry import PluginRegistry
from .utils import ClufterError, hybridproperty

log = logging.getLogger(__name__)


class CommandError(ClufterError):
    pass


class commands(PluginRegistry):
    """Command registry (to be used as a metaclass for commands)"""
    pass


class Command(object):
    """Base for commands, i.e., encapsulations of filter chains"""
    __metaclass__ = commands

    def __init__(self, *filter_chain):
        self._filter_chain = filter_chain

    @hybridproperty
    def filter_chain(this):
        """Chain of filter identifiers/classes for the command"""
        return this._filter_chain

    @classmethod
    def deco(cls, *filter_chain):
        """Decorator as an easy factory of actual commands"""
        def deco_fnc(fnc):
            log.debug("Command: deco for {0}"
                      .format(fnc))
            attrs = {
                '__module__': fnc.__module__,
                '__doc__': fnc.__doc__,
                '_filter_chain': filter_chain,
                '_fnc': staticmethod(fnc),
            }
            # optimization: shorten type() -> new() -> probe
            ret = cls.probe(fnc.__name__, (cls, ), attrs)
            return ret
        return deco_fnc
