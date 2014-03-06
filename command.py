# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base command stuff (TBD)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from itertools import izip_longest
from optparse import SUPPRESS_HELP
from platform import system, linux_distribution

from .command_context import CommandContext
from .error import ClufterError, \
                   EC
from .filter import Filter
from .plugin_registry import PluginRegistry
from .utils import any2iter, \
                   args2sgpl, \
                   args2tuple, \
                   apply_aggregation_preserving_depth, \
                   apply_intercalate, \
                   apply_loose_zip_preserving_depth, \
                   bifilter, \
                   func_defaults_varnames, \
                   head_tail, \
                   hybridproperty, \
                   longopt_letters_reprio, \
                   selfaware, \
                   tuplist, \
                   tailshake, \
                   zip_empty

log = logging.getLogger(__name__)

protodecl = lambda x: len(x) == 2 and isinstance(x[0], Filter)

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
        self._filter_chain_analysis = None  # will be dict

    #
    # filter chain related
    #

    @property
    def filter_chain_analysis(self):
        if self._filter_chain_analysis is None:
            filter_chain = self._filter_chain
            self._filter_chain_analysis = self.analyse_chain(filter_chain)
        return self._filter_chain_analysis

    @staticmethod
    @selfaware
    def analyse_chain(me, filter_chain, analysis_acc=None):
        """Given the filter chain, return filter backtrack and terminal chain

        This is done by recursive traversal.  Also check that the graph is
        actually connected wrt. protocols compatibility between each of
        adjacent filters is performed.

        XXX: mentioned check doesn't know about CompositeFormat and
             the connected magic, yet
        """
        new = analysis_acc is None
        if new:
            analysis_acc = dict(filter_backtrack={},
                                terminal_chain=[[]])
        filter_backtrack = analysis_acc['filter_backtrack']
        terminal_chain = analysis_acc['terminal_chain'][-1]

        assert tuplist(filter_chain)
        # PASSDOWN or FILTERS
        pass_through, filter_chain = head_tail(*filter_chain) \
                                     if isinstance(filter_chain, tuple) \
                                     and len(filter_chain) > 1 \
                                     else (None, filter_chain)
        for i in filter_chain:
            i, i_tail = head_tail(i)
            bt = filter_backtrack.setdefault(i, {})
            if new or not (bt or i_tail):
                # new for UPFILTERs, which are also terminals (input ones)
                terminal_chain.append(i)
            if pass_through:
                if pass_through in bt:
                    raise CommandError(me,
                        "filter `{0}' is feeded by `{1}' more than once",
                        i.__class__.__name__, pass_through.__class__.__name__
                    )
                common_protocols = sorted(
                    reduce(
                        set.intersection,
                        map(set, (pass_through.out_format._protocols,
                                  i.in_format._protocols))
                    ),
                    key=lambda x:
                        int(x == pass_through.out_format.native_protocol)
                        + int(x == i.in_format.native_protocol)
                )
                if not common_protocols:
                    raise CommandError(me,
                        "filter `{0}' and its feeder `{1}' have no protocol"
                        " in common",
                        i.__class__.__name__, pass_through.__class__.__name__
                    )
                bt[pass_through] = common_protocols
            if i_tail:
                # PASSDOWN
                # this uses a dirty trick of exploiting the end of the list
                # as a sort of a stack, where the per-recursion-level result
                # is available for the caller (who is also responsible for
                # preparing a new list here for callee to fill) so it can
                # move it to the right position afterwards
                analysis_acc['terminal_chain'].append([])  # not terminal_chain
                me((i, ) + i_tail, analysis_acc)
                terminal_chain.append(analysis_acc['terminal_chain'].pop())
            elif new:
                # yes, terminal UPFILTER is tracked twice as terminal (I/O)
                terminal_chain.append(i)

        return analysis_acc

    #
    # self-introspection (arguments, description, options)
    #

    def _figure_fnc_defaults_varnames(self):
        """Dissect self._fnc to arg defaults (dict) + all arg names (tuple)"""
        try:
            fnc = self._fnc
        except:
            raise CommandError(self, "Subclass does not implement _fnc")
        if self._fnc_defaults_varnames is None:
            self._fnc_defaults_varnames = func_defaults_varnames(fnc, skip=1)
        return self._fnc_defaults_varnames

    @classmethod
    def _figure_parser_desc_opts(cls, fnc_defaults, fnc_varnames):
        readopts, shortopts, options = False, {}, []
        description = []
        fnc_varnames = set(fnc_varnames)

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
                    fnc_varnames.remove(optname)
                    short_aliases = shortopts.setdefault(optname[0], [])
                    assert optname not in short_aliases
                    short_aliases.append(len(options))
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
                    options.append([["--" + optname], opt])
            elif line.lower().startswith('options:'):
                readopts = True
            else:
                description.append(line)

        for short, aliases in shortopts.iteritems():  # foreach in ideal shorts
            for i, alias in enumerate(aliases):  # foreach in conflicting ones
                for c in longopt_letters_reprio(options[alias][0][0]):
                    if c not in shortopts or i == 0:
                        use = '-' + c
                        break
                else:
                    log.warning("Could not find short option for `{0}'"
                                .format(options[alias][0]))
                    break
                options[alias][0].append(use)

        # unofficial/unsupported ones
        for var in fnc_varnames:
            options.append([[var], dict(help=SUPPRESS_HELP)])

        description = description[:-1] if not description[-1] else description
        description = '\n'.join(description)
        return description, options

    @property
    def parser_desc_opts(self):
        """Parse docstring as description + Option constructor args list"""
        if self._desc_opts is None:
            self._desc_opts = self._figure_parser_desc_opts(
                *self._figure_fnc_defaults_varnames()
            )
        return self._desc_opts

    #
    # execution related
    #

    @staticmethod
    @selfaware
    def _iochain_check_terminals(me, io_chain, terminal_chain):
        # validate "terminal filter chain" vs "io chain"
        # 1. "shapes" match incl. input (head)/output (tail) protocol match
        if len(terminal_chain) == 1 and len(io_chain) == len(terminal_chain[0]):
            # see `deco`: 2.
            io_chain = args2tuple(io_chain)
        to_check = apply_loose_zip_preserving_depth(terminal_chain, io_chain)
        for to_check_inner in to_check:
            for passno, check in enumerate(head_tail(to_check_inner)):
                checked = apply_aggregation_preserving_depth(
                    lambda i:
                        head_tail(i[1])[0] not in getattr(i[0],
                            ('in_format', 'out_format')[passno])._protocols
                            and str(head_tail(i[1])[0]) or None
                        if protodecl(i) else i if any(i) else None
                )(to_check_inner[passno])
                checked_flat = apply_intercalate((checked,))
                for order, cmd in filter(lambda (i, x): x,
                                         enumerate(checked_flat)):
                    raise CommandError(me,
                        "filter resolution #{0} of {1}: {2}", order + 1,
                        ('input', 'output')[passno],
                        "filter/io chain definition (shape) mismatch"
                        if isinstance(cmd, (type(zip_empty), Filter))
                        else "`{0}' protocol not suitable".format(cmd)
                    )
        return to_check

    @classmethod
    def _iochain_proceed(cls, cmd_ctxt, io_chain):
        # currently works sequentially, jumping through the terminals in-order;
        # when any of them (apparently the output one) hasn't its prerequisites
        # (i.e., input data) satisfied, the run is restarted with first
        # producing such data (which are output of another filter feeding
        # the one in question) -- this can be repeated multiple times if
        # there is a longer chain forming such a gap
        # -- this is certainly needlessly slow method, but there is a hope
        #    the same approach could be applied when parallelizing the stuff
        # XXX could be made more robust (ordering still not as strict as it
        #                                should)
        # XXX some parts could be performed in parallel (requires previous
        #     item so to prevent deadlocks on cond. var. wait)
        #     - see also `heapq` standard module
        filter_backtrack = cmd_ctxt['filter_chain_analysis']['filter_backtrack']
        terminal_chain = cmd_ctxt['filter_chain_analysis']['terminal_chain']
        terminals = apply_intercalate(terminal_chain)

        terminal_chain = cls._iochain_check_terminals(io_chain, terminal_chain)

        input_cache = cmd_ctxt.setdefault('input_cache', {})
        worklist = list(reversed(tailshake(terminal_chain,
                                           partitioner=lambda x:
                                           not (tuplist(x)) or protodecl(x))))
        while worklist:
            flt, io_decl = worklist.pop()
            flt_ctxt = cmd_ctxt.ensure_filter(flt)
            if not filter_backtrack[flt] and not flt_ctxt['out']:
                # INFILTER in in-mode
                log.debug("Run `{0}' filter with `{1}' io decl. as INFILTER"
                          .format(flt.__class__.__name__, io_decl))
                if io_decl in input_cache:
                    in_obj = input_cache[io_decl]
                else:
                    in_obj = flt.in_format.as_instance(*io_decl)
                    input_cache[io_decl] = in_obj
            elif filter_backtrack[flt] and not flt_ctxt['out']:
                # not INFILTER in either mode (nor output already precomputed?)
                log.debug("Run `{0}' filter with `{1}' io decl. as DOWNFILTER"
                          .format(flt.__class__.__name__, io_decl))
                inputs = map(lambda x: cmd_ctxt.filter(x.__class__.__name__)['out'],
                             filter_backtrack[flt])
                notyet, ok = bifilter(lambda x:
                                  cmd_ctxt.filter(x.__class__.__name__)['out'] is None,
                                  filter_backtrack[flt])
                if notyet:
                    log.debug("Backtrack with inclusion of {0} to feed `{1}'"
                              .format(', '.join("`{0}'"
                                      .format(nt.__class__.__name__)
                                              for nt in notyet),
                                      flt.__class__.__name__))
                    worklist.append((flt, io_decl))
                    worklist.extend(reversed(tuple((ny, None)
                                             for ny in notyet)))
                    continue
                assert all(inputs)
                in_obj = flt.in_format.as_instance(*inputs)
            if not flt_ctxt['out'] or flt not in terminals:
                if not flt_ctxt['out']:
                    flt_ctxt['out'] = flt(in_obj, flt_ctxt)
                if flt not in terminals or not filter_backtrack[flt]:
                    continue
            # output time!  (INFILTER terminal listed twice in io_chain)
            log.debug("Run `{0}' filter with `{1}' io decl. as TERMINAL"
                      .format(flt.__class__.__name__, io_decl))
            # XXX following could be stored somewhere, but rather pointless
            flt_ctxt['out'](*io_decl)
        return EC.EXIT_SUCCESS  # XXX some better decision?

    def __call__(self, opts, args=None, cmd_ctxt=None):
        """Proceed the command"""
        ec = EC.EXIT_SUCCESS
        fnc_defaults, fnc_varnames = self._figure_fnc_defaults_varnames()
        kwargs = {}
        if args:
            if '::' in args[0]:
                # desugaring, which is useful mainly if non-contiguous sequence
                # of value-based options need to be specified
                args = args[0].split('::') + args[1:]
            args.reverse()  # we will be poping from the end
        for v in fnc_varnames:
            opt = getattr(opts, v, None)
            if opt is not None and opt != fnc_defaults.get(v, None):
                kwargs[v] = getattr(opts, v)
                continue
            if args:
                cur = args.pop()
                if cur != '':
                    kwargs[v] = cur
                    continue
            if getattr(opts, v, None) != fnc_defaults.get(v, None):
                raise CommandError(self, "missing value for `{0}'", v)
        cmd_ctxt = cmd_ctxt or CommandContext()
        cmd_ctxt.ensure_filters(apply_intercalate(self._filter_chain))
        cmd_ctxt['filter_chain_analysis'] = self.filter_chain_analysis
        io_driver = any2iter(self._fnc(cmd_ctxt, **kwargs))
        io_handler = (self._iochain_proceed, lambda c, ec=EC.EXIT_SUCCESS: ec)
        io_driver_map = izip_longest(io_driver, io_handler)
        for driver, handler in io_driver_map:
            driver = () if driver is None else (driver, )
            ec = handler(cmd_ctxt, *driver)
            if ec != EC.EXIT_SUCCESS:
                break
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

        where, for filter x (in {A, ..., D, O, P} for the example at hand):

            EXPRESSION  ::= UPFILTERS
            UPFILTERS   ::= TERMINAL | ( FILTERS )
            FILTERS     ::= FILTER, | FILTERS FILTER
            FILTER      ::= PASSDOWN | TERMINAL
            PASSDOWN    ::= (TERMINAL, DOWNFILTERS)
            TERMINAL    ::= x
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
            - to make it explicit, the graph is expressed in depth-first
              (or DFS) manner


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


class CommandAlias(object):
    """Way to define either static or dynamic command alias"""
    __metaclass__ = commands

    _system = system()
    _system_extra = linux_distribution(full_distribution_name=0) \
                    if _system == 'Linux' else ()

    @classmethod
    def deco(outer_cls, decl):
        if not hasattr(decl, '__call__'):
            assert issubclass(decl, Command)
            fnc = lambda **kwargs: decl
        else:
            fnc = decl
        log.debug("CommandAlias: deco for {0}".format(fnc))

        def new(cls, cmds):
            # XXX really pass mutable cmds dict?
            use_obj = fnc(cmds, outer_cls._system, outer_cls._system_extra)
            if not isinstance(use_obj, Command):
                assert isinstance(use_obj, basestring)
                use_obj = cmds[use_obj]
                assert isinstance(use_obj, Command)
            return use_obj

        attrs = {
            '__module__': fnc.__module__,
            '__new__': new,
        }
        # optimization: shorten type() -> new() -> probe
        ret = outer_cls.probe(fnc.__name__, (outer_cls, ), attrs)
        return ret
