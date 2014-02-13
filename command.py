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
from .utils import args2sgpl, \
                   apply_aggregation_preserving_depth, \
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
    """Base for commands, i.e., encapsulations of filter chains

    Also see the docstring for `deco`.
    """
    __metaclass__ = commands

    @hybridproperty
    def filter_chain(this):
        """Chain of filter identifiers/classes for the command"""
        return this._filter_chain

    def __init__(self, *filter_chain):
        self._filter_chain = filter_chain  # already resolved
        # following will all be resolved lazily, on-demand;
        # all of these could be evaluated upon instantiation immediately,
        # but this is not the right thing to do due to potentially many
        # commands being instantiated initially, while presumably only one
        # of them will be run later on
        self._desc_opts = None
        self._fnc_defaults_varnames = None

    #
    # self-introspection (arguments, description, options)
    #

    def _figure_fnc_defaults_varnames(self, fnc=None):
        fnc = fnc or getattr(self, '_fnc', None)
        if self._fnc_defaults_varnames is None:
            if not fnc:
                self._fnc_defaults_varnames = {}, ()
            else:
                self._fnc_defaults_varnames = func_defaults_varnames(fnc)
        return self._fnc_defaults_varnames

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
                        default = fnc_defaults[optname]
                        if default in (True, False):
                            opt['action'] = ('store_true',
                                             'store_false')[int(default)]
                            opt['help'] += " [{0}]".format('enabled' if default
                                                           else 'disabled')
                        else:
                            opt['help'] += " [%default]"
                        opt['default'] = default
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
        if self._desc_opts is None:
            self._desc_opts = self._figure_parser_desc_opts(
                *self._figure_fnc_defaults_varnames()
            )
        return self._desc_opts

    #
    # execution related
    #

    def __call__(self, opts, args=None):
        """Proceed the command"""
        ec = EC.EXIT_SUCCESS
        fnc_defaults, fnc_varnames = self._figure_fnc_defaults_varnames()
        kwargs = {}
        for v in fnc_varnames:
            if getattr(opts, v, None) is not None:
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
        """Decorator as an easy factory of actual commands

        Parameters:
            filter_chain: particular scalars and vectors (variable depth)
                          representing graph of filters that form this command

        Note on graph representation within filter_chain:

                 __B    ___D
                /      /
            A--<___C--<             in ----------------> out
                       \
            O___________>--P


        graph with letter denoting the filters and with the left->right
        direction of flow from the inputs towards outputs (final outputs
        at terminals: B, D, P), is encoded as:

            ((A, B, (C, D, P)), (O, P), )

        where, for filter X (in {A, ..., D, O, P} for the example at hand):

            EXPRESSION  ::= UPFILTERS
            UPFILTERS   ::= TERMINAL | ( FILTERS )
            FILTERS     ::= FILTER, | FILTERS FILTER
            FILTER      ::= TERMINAL | PASSDOWN
            TERMINAL    ::= X
            PASSDOWN    ::= (X, DOWNFILTERS)
            DOWNFILTERS ::= FILTERS

        where:
            - {UP,DOWN}FILTERS dichotomy is present only as
              a forward-reference for easier explanation
            - there is a limitation such that each filter can
              be contained as at most one node in the graph as above
              (this corresponds to the notion of inputs merge for
              the filter, as otherwise there would be ambiguity:
              in the selected notation, can the filter occurences stand
              for unique nodes?  remember, filters as singletons)
            - UPFILTERS ::= TERMINAL is a syntactic sugar exploiting
              unambiguity in converting such expression as (TERMINAL, )


        Note on the decorated function:
            It should either return an iterable or behave itself as a generator
            yielding the items (at once) and on subsequent round triggering
            some postprocessing (still from decorated function's perspective).
            The items coming from the function encodes the protocols at
            the input(s) and the output(s) of the filter graph encoded in
            `filter_chain` and ought to reflect this processing construct
            as follows:
                1. for each UPFILTER in order, there is a tuple of two parts
                   1b. first part denotes the input (only single decl)
                   2b. second part denotes the output, which follows the
                       branch of filter chain pertaining the particular
                       UPFILTER, and can be either scalar or (arbitrarily)
                       nested iterable to match that filter chain branch
                       (proper nesting is not needed, only the order is
                       important, see point 4.)
                2. if there is just one UPFILTER, the toplevel definition
                   can be just the respective un-nested item, as this case
                   is easy to distinguish and apply un-sugaring if applicable
                3. when there is the same filter down the line shared by
                   2+ UPFILTERs (cf. "limitation such that each filter" above)
                   the respective protocol encoding is expected just once
                   within the first(!) respective UPFILTER definition
                #-- not yet, if ever, as it is opposed by good diagnostics --
                #4. nesting of the second part of the tuple (2b.) is not
                #   strictly needed and only the order is important,
                #   as the association is performed on intercalated chains
                #   anyway (note that this is orthogonal to simplification 2.)

            for the graph above, it would be, e.g.,:

            (('Aproto', 'a-in.txt'),
                (('Bproto', 'b-out.txt'), (('Dproto', 'd-out.txt'), ('Pproto')))),
            (('Oproto', 'e-in.txt'), )

            #which, as per point 4., can be further simplified as:

            #(('Aproto', 'a-in.txt'),
            #    ('Bproto', 'b-out.txt'), ('Dproto', 'd-out.txt'), ('Pproto')),
            #(('Oproto', 'e-in.txt'), )
        """
        def deco_fnc(fnc):
            log.debug("Command: deco for {0}"
                      .format(fnc))
            attrs = {
                '__module__': fnc.__module__,
                '__doc__': fnc.__doc__,
                '_filter_chain': args2sgpl(filter_chain),
                '_fnc': staticmethod(fnc),
            }
            # optimization: shorten type() -> new() -> probe
            ret = cls.probe(fnc.__name__, (cls, ), attrs)
            return ret
        return deco_fnc
