# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base command stuff (TBD)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from optparse import make_option, SUPPRESS_HELP

from .error import ClufterError, \
                   EC
from .filter import Filter
from .plugin_registry import PluginRegistry
from .utils import apply_aggregation_preserving_depth, \
                   apply_intercalate, \
                   apply_loose_zip_preserving_depth, \
                   func_defaults_varnames, \
                   head_tail, \
                   hybridproperty, \
                   zip_empty

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
        self._filter_chain = filter_chain  # already resolved
        self._desc, self._options = None, None  # later on-demand
        self._fnc_defaults, self._fnc_varnames = None, None  # ditto

    def _figure_func_defaults_varnames(self, fnc=None):
        fnc = fnc or getattr(self, '_fnc', None)
        if self._fnc_defaults is None or self._fnc_varnames is None:
            if not fnc:
                self._fnc_defaults, self._fnc_varnames = {}, ()
            else:
                self._fnc_defaults, self._fnc_varnames = \
                    func_defaults_varnames(fnc)
        return self._fnc_defaults, self._fnc_varnames

    @classmethod
    def _figure_parser_desc_opts(cls, fnc_defaults, fnc_varnames):
        readopts, optionset, options = False, set(), []
        description = []

        for line in cls.__doc__.splitlines():
            line = line.lstrip()
            if readopts:
                if not line:
                    continue
                line = line.replace('\t', ' ')
                optname, optdesc = head_tail(line.split(' ', 1))  # 2nd->tuple
                if not all((optname, optdesc)) or optname not in fnc_varnames:
                    log.debug("Bad option line: {0}".format(line))
                else:
                    log.debug("Command `{0}', found option `{1}'".format(
                        cls.name, optname
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

        for var in fnc_varnames:
            if var not in optionset:
                options.append(make_option("--{0}".format(var),
                                           help=SUPPRESS_HELP))

        description = description[:-1] if not description[-1] else description
        description = '\n'.join(description)
        return description, options

    @property
    def parser_desc_opts(self):
        """Parse docstring as description + optparse.Option instances list"""
        if self._desc is None or self._options is None:
            self._desc, self._options = self._figure_parser_desc_opts(
                *self._figure_func_defaults_varnames()
            )
        return self._desc, self._options

    @hybridproperty
    def filter_chain(this):
        """Chain of filter identifiers/classes for the command"""
        return this._filter_chain

    def __call__(self, opts, args=None):
        """Proceed the command"""
        ec = EC.EXIT_SUCCESS
        fnc_defaults, fnc_varnames = self._figure_func_defaults_varnames()
        kwargs = {}
        for v in fnc_varnames:
            if hasattr(opts, v):
                kwargs[v] = getattr(opts, v)
        io_chain = self._fnc(**kwargs)
        ##print io_chain
        ##from .utils import apply_aggregation_preserving_passing_depth
        ##print apply_aggregation_preserving_passing_depth(
        ##    lambda x, d: ('\n' + d * ' ') + (' ').join(x)
        ##)(io_chain)
        # validate io_chain vs chain
        # 1. "shapes" match incl. input (head)/output (tail) protocol match
        to_check = head_tail(
            apply_loose_zip_preserving_depth(self.filter_chain, io_chain)
        )
        for passno, check in enumerate(to_check):
            checked = apply_aggregation_preserving_depth(
                lambda i:
                    head_tail(i[1])[0] not in getattr(i[0],
                        ('in_format', 'out_format')[passno])._protocols
                        and head_tail(i[1])[0] or None
                    if len(i) == 2 and isinstance(i[0], Filter)
                    else i if any(i) else None
            )(to_check[passno])
            for order, cmd in filter(lambda (i, x): x,
                                     enumerate(apply_intercalate((checked,)))):
                raise CommandError(self, "filter resolution #{0} of {1}: {2}",
                                   order + 1, ('input', 'output')[passno],
                                   "`{0}' protocol not recognized".format(cmd)
                                   if cmd is not zip_empty else "filter/io"
                                   " chain definition (shape) mismatch")
        # TODO
        #   2. I/O formats path(s) through the graph exist(s)
        #   3. some per-filter validations?
        #   - could some initial steps be done earlier?
        # - perform the chain
        #   - [advanced] threading for parallel branches?
        return ec

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
