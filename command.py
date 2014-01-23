# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base command stuff (TBD)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from optparse import make_option

from .plugin_registry import PluginRegistry
from .utils import ClufterError, head_tail, hybridproperty

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
        self._desc, self._options = None, None  # later on-demand

    def parser_desc_opts(self, cmd=None):
        """Parse docstring as description + optparse.Option instances list"""
        if self._desc and self._options:
            return self._desc, self._options
        fnc_defaults, fnc_varnames = dict(zip(
            self._fnc.func_code.co_varnames[-len(self._fnc.func_defaults):],
            self._fnc.func_defaults
        )), self._fnc.func_code.co_varnames

        readopts, optionset, options = False, set(), []
        description = []

        for line in self.__doc__.splitlines():
            line = line.lstrip()
            if readopts:
                if not line:
                    continue
                line = line.replace('\t', ' ')
                optname, optdesc = head_tail(*line.split(' ', 1))  # 2nd->tuple
                if not all((optname, optdesc)) or optname not in fnc_varnames:
                    log.debug("Bad option line: {0}".format(line))
                else:
                    log.debug("Command `{0}', found option `{1}'".format(
                        self.__class__.name, optname
                    ))
                    assert optname not in optionset
                    optionset.add(optname)
                    opt = {}
                    opt['help'] = optdesc[0].strip()
                    if optname in fnc_defaults:  # default if known
                        opt['default'] = fnc_defaults[optname]
                        opt['help'] += " [%default]"
                    options.append(make_option("--{0}".format(optname), **opt))
            elif line.lower().startswith('options:'):
                readopts = True
            else:
                description.append(line)
        description = description[:-1] if not description[-1] else description
        description = '\n'.join(description)
        self._description, self._options = description, options
        return description, options

    def parse_args(self, script, cmd, **kwargs):
        """Perform per-command options/arguments parsing"""
        if not self._option_parser:
            self._option_parser = self._make_option_parser(script, cmd)
        return self._option_parser.parse_args(**kwargs)

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
