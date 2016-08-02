# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base command stuff (TBD)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from collections import MutableMapping
from itertools import izip_longest
from logging import getLogger
from optparse import OptionParser
from sys import stderr, stdin, stdout
from time import time

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from .command_context import CommandContext
from .error import ClufterError, \
                   EC
from .filter import Filter, CMD_HELP_OPTSEP_COMMON
from .format import FormatError, SimpleFormat
from .plugin_registry import PluginRegistry
from .protocol import protodictval
from .utils import any2iter, \
                   areinstancesupto, \
                   args2tuple, \
                   filterdict_keep, \
                   head_tail, \
                   hybridproperty, \
                   nonetype, \
                   selfaware, \
                   tuplist
from .utils_func import apply_aggregation_preserving_depth, \
                        apply_intercalate, \
                        apply_loose_zip_preserving_depth, \
                        apply_preserving_depth, \
                        bifilter, \
                        tailshake, \
                        zip_empty
from .utils_prog import FancyOutput, \
                        cli_decor, \
                        longopt_letters_reprio, \
                        defer_common

log = getLogger(__name__)

protodecl = lambda x: len(x) == 2 and isinstance(x[0], Filter)

# expected to be lowercase for more straightforward case-insensitive comparison
CMD_HELP_OPTSEP_PRIMARY = 'options:'
CMD_HELP_OPTSEP_COMMON =  CMD_HELP_OPTSEP_COMMON.lower()


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

    @classmethod
    def _resolve_filter_chain(cls, filters):
        res_input = cls._filter_chain
        res_output = apply_preserving_depth(filters.get)(res_input)
        if apply_aggregation_preserving_depth(all)(res_output):
            log.debug("resolve at `{0}' command: `{1}' -> {2}"
                      .format(cls.name, repr(res_input), repr(res_output)))
            return res_output
        # drop the command if cannot resolve any of the filters
        res_input = apply_intercalate(res_input)
        map(lambda (i, x): log.warning("Resolve at `{0}' command:"
                                       " `{1}' (#{2}) filter fail"
                                       .format(cls.name, res_input[i], i)),
            filter(lambda (i, x): not(x),
                   enumerate(apply_intercalate(res_output))))
        return None

    @hybridproperty
    def filter_chain(this):
        """Chain of filter identifiers/classes for the command"""
        return this._filter_chain

    def __new__(cls, filters, *args):
        filter_chain = cls._resolve_filter_chain(filters)
        if filter_chain is None:
            return None
        self = super(Command, cls).__new__(cls)
        self._filter_chain = filter_chain
        self._filters = OrderedDict((f.__class__.name, f) for f in
                                    apply_intercalate(filter_chain))
        fnc_defaults, fnc_varnames = self._fnc_defaults_varnames
        for varname, default in fnc_defaults.iteritems():
            if not isinstance(default, basestring):
                continue
            try:
                # early/static interpolation of defaults ~ filters' constants
                fnc_defaults[varname] = default.format(**self._filters)
            except AttributeError:
                pass
        self._fnc_defaults_varnames = fnc_defaults, fnc_varnames
        # following will all be resolved lazily, on-demand;
        # all of these could be evaluated upon instantiation immediately,
        # but this is not the right thing to do due to potentially many
        # commands being instantiated initially, while presumably only one
        # of them will be run later on
        self._desc_opts = None
        self._filter_chain_analysis = None  # will be dict
        return self

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

        assert tuplist(filter_chain) and filter_chain
        # PASSDOWN or FILTERS
        passed_filter_length = len(filter_chain)
        pass_through, filter_chain = head_tail(*filter_chain) \
                                     if len(filter_chain) > 1 \
                                     and (not isinstance(filter_chain[0], tuple) \
                                     or len(filter_chain[0]) < 2) \
                                     else (None, filter_chain)
        # the condition handles differences between:
        #    ('A',
        #        ('B'),
        #        ('C'))
        # and
        #    ('A',
        #        ('B',
        #            ('C')))
        # XXX: regardless if isinstance(filter_chain[1], tuple)
        if len(filter_chain) >= passed_filter_length + int(new):
            filter_chain = (filter_chain, )
        for i_origin in filter_chain:
            if not i_origin:
                continue
            i, i_tail = head_tail(i_origin)
            # bt denotes filters feeding this one
            bt = filter_backtrack.setdefault(i, OrderedDict())
            if new or not (bt or i_tail):  # preorder
                # new for UPFILTERs, which are also terminals (input ones)
                terminal_chain.append(i)
            if pass_through:
                if pass_through in bt:
                    raise CommandError(me,
                        "filter `{0}' is feeded by `{1}' more than once",
                        i.__class__.__name__, pass_through.__class__.__name__
                    )
                common_protocols = None  # for when CompositeFormat involved
                if (hasattr(pass_through.out_format, '_protocols')
                    and hasattr(i.in_format, '_protocols')):
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
                # see "the condition handles differences between" comment
                me(i_origin, analysis_acc)
                # postorder
                ret = analysis_acc['terminal_chain'].pop()
                if ret:
                    # not a another use of already used (merging) filter
                    terminal_chain.append(ret)
            elif new:
                # yes, terminal UPFILTER is tracked twice as terminal (I/O)
                terminal_chain.append(i)

        return analysis_acc

    #
    # self-introspection (arguments, description, options)
    #

    def _figure_parser_opt_dumpnoop(self, options, shortopts):
        choices = []
        for fname, f in self._filters.iteritems():
            if issubclass(f.in_format.__class__, f.out_format.__class__):
                choices.append(fname)
        # XXX NOOPizing doesn't make sense for input filters?
        debug_opts = (
            ('noop', False,
             "debug only: NOOPize filter (2+: repeat) [none out of %choices]"),
            ('dump', True,
             "debug only: dump (intermediate) output of the filter (2+: repeat)"
             " [none out of %choices]"),
        )
        for optname_used, universal, help_text in debug_opts:
            short_aliases = shortopts.setdefault(optname_used[0], [])
            assert optname_used not in \
                (options[i][0][0] for i in short_aliases)
            log.debug("choices: {0}".format(choices))
            opt = dict(
                action='append',
                choices=choices + ['ANY'] if universal else choices,
                default=[],
                expert=True,
                help=help_text,
            )
            options.append([["--" + optname_used], opt])

    def _figure_parser_opt_unofficial(self, options, shortopts, fnc_varnames):
        # unofficial/unsupported ones
        for var in fnc_varnames:
            optname_used = cli_decor(var)
            options.append([["--" + optname_used], dict(
                expert=True,
                help="(undocumented expert option)",
            )])

    def _figure_parser_desc_opts(self, fnc_defaults, fnc_varnames,
                                 opt_group=None):
        readopts, common_tail = False, False
        shortopts, options, expert =  {}, [], []
        description = []
        fnc_varnames = set(fnc_varnames)
        opt_group = opt_group or OptionParser()

        for line in self.__doc__.splitlines():
            line = line.lstrip()
            if readopts:
                if not line:
                    continue
                if line.lower().startswith(CMD_HELP_OPTSEP_COMMON):
                    common_tail = True
                    continue
                line = line.replace('\t', ' ')
                optname, optdesc = head_tail(line.split(' ', 1))  # 2nd->tuple
                if not all((optname, optdesc)) or optname not in fnc_varnames:
                    log.warning("Bad option line: {0}".format(line))
                else:
                    target = expert if optname.startswith('_') else options
                    optname_used = cli_decor(optname.lstrip('_'))
                    log.debug("Command `{0}', found option `{1}' ({2})".format(
                        self.__class__.name, optname_used, optname
                    ))
                    fnc_varnames.remove(optname)
                    short_aliases = shortopts.setdefault(optname_used[0], [])
                    opt = {}
                    if target is expert:
                        opt['expert'] = True
                        opt['dest'] = optname  # (un)decor just works, '_' not
                    elif not common_tail:
                        assert optname_used not in \
                            (options[i][0][0] for i in short_aliases)
                        short_aliases.append(len(options))  # as an index
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
                    target.append([["--" + optname_used], opt])
            elif line.lower().startswith(CMD_HELP_OPTSEP_PRIMARY):
                readopts = True
            else:
                description.append(line)

        for short, aliases in shortopts.iteritems():  # foreach in ideal shorts
            for i, alias in enumerate(aliases):  # foreach in conflicting ones
                for c in longopt_letters_reprio(options[alias][0][0]):
                    use = '-' + c
                    if opt_group.has_option(use):
                        continue
                    if c not in shortopts or i == 0:
                        break
                else:
                    log.info("Could not find short option for `{0}'"
                             .format(options[alias][0]))
                    break
                options[alias][0].append(use)

        self._figure_parser_opt_dumpnoop(options, shortopts)
        options.extend(expert)
        self._figure_parser_opt_unofficial(options, shortopts, fnc_varnames)

        description = description[:-1] if not description[-1] else description
        description = '\n'.join(description)
        return description, options

    def parser_desc_opts(self, opt_group=None):
        """Parse docstring as description + Option constructor args list"""
        if self._desc_opts is None:
            self._desc_opts = self._figure_parser_desc_opts(
                *self._fnc_defaults_varnames, opt_group=opt_group
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
                        head_tail(protodictval(i[1]))[0] not in getattr(i[0],
                            ('in_format', 'out_format')[passno])._protocols
                            and str(head_tail(i[1])[0]) or None
                        if protodecl(i) else i if any(i) else None
                )(check)
                checked_flat = apply_intercalate((checked,))
                for order, proto in filter(lambda (i, x): x,
                                           enumerate(checked_flat)):
                    if proto is zip_empty:
                        continue
                    raise CommandError(me,
                        "filter resolution #{0} of {1}: {2}", order + 1,
                        ('input', 'output')[passno],
                        "`{0}' filter/io chain definition (shape) mismatch"
                        .format(proto)
                        if isinstance(proto, (type(zip_empty), Filter))
                        else "`{0}' protocol not suitable".format(proto)
                    )
        return to_check

    def _iochain_proceed(self, cmd_ctxt, io_chain):
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

        terminal_chain = self._iochain_check_terminals(io_chain, terminal_chain)

        native_fds = dict((f.fileno(), f) for f in (stderr, stdin, stdout))
        magic_fds = native_fds.copy()
        input_cache = cmd_ctxt.setdefault('input_cache', {}, bypass=True)
        worklist = list(reversed(tailshake(terminal_chain,
                                           partitioner=lambda x:
                                           not (tuplist(x)) or protodecl(x))))
        # if any "EMPTY" (zip_empty) value present, respective class name ~ str
        unused, tstmp = {}, hex(int(time()))[2:]
        while worklist:
            workitem = worklist.pop()
            if workitem == zip_empty:
                log.debug("Worklist: EMPTY value observed, skipped")
                continue
            flt, io_decl = workitem
            io_decl_use = protodictval(io_decl)
            io_decl, passout = (io_decl_use, unused if io_decl_use is io_decl
                                             else io_decl)
            flt_ctxt = cmd_ctxt.ensure_filter(flt)
            with flt_ctxt.prevented_taint():
                fmt_kws = filterdict_keep(flt_ctxt, *flt.in_format.context)
            if not filter_backtrack[flt] and 'out' not in flt_ctxt:
                # INFILTER in in-mode
                log.debug("Run `{0}' filter with `{1}' io decl. as INFILTER"
                          .format(flt.__class__.__name__, io_decl))
                if io_decl in input_cache:
                    in_obj = input_cache[io_decl]
                else:
                    with cmd_ctxt.prevented_taint():
                        io_decl = SimpleFormat.io_decl_specials(
                                      io_decl, 1, magic_fds,
                                      cmd_ctxt['__filters__']
                        )
                        in_obj = flt.in_format.as_instance(*io_decl, **fmt_kws)
                    input_cache[io_decl] = flt_ctxt['in'] = in_obj
            elif filter_backtrack[flt] and 'out' not in flt_ctxt:
                # not INFILTER in either mode (nor output already precomputed?)
                log.debug("Run `{0}' filter with `{1}' io decl. as DOWNFILTER"
                          .format(flt.__class__.__name__, io_decl))
                ok, notyet = bifilter(lambda x: 'out' in
                                        cmd_ctxt.filter(x.__class__.__name__),
                                      filter_backtrack[flt])
                if notyet:
                    log.debug("Backtrack with inclusion of {0} to feed `{1}'"
                              .format(', '.join("`{0}'"
                                      .format(ny.__class__.__name__)
                                              for ny in notyet),
                                      flt.__class__.__name__))
                    worklist.append((flt, io_decl if passout is unused
                                          else passout))
                    worklist.extend(reversed(tuple((ny, None)
                                             for ny in notyet)))
                    continue

                inputs = map(lambda x: cmd_ctxt.filter(x.__class__.__name__)
                                       .get('out'),
                             filter_backtrack[flt])
                assert all(inputs)
                with cmd_ctxt.prevented_taint():
                    in_obj = flt.in_format.as_instance(*inputs, **fmt_kws)
                flt_ctxt['in'] = in_obj  # referred in interpolation -> a bug?
            if 'out' not in flt_ctxt or flt not in terminals:
                if 'out' not in flt_ctxt:
                    if flt.__class__.name in cmd_ctxt['filter_noop']:
                        ret = in_obj
                    else:
                        with cmd_ctxt.prevented_taint():
                            ret = flt(in_obj, flt_ctxt)
                    flt_ctxt['out'] = ret
                if flt not in terminals or not filter_backtrack[flt]:
                    if (flt.__class__.name in cmd_ctxt['filter_dump']
                        or 'ANY' in cmd_ctxt['filter_dump']):
                        try:
                            fn = 'dump-{0}-{1}-{2}'.format(
                                flt.__class__.name,
                                flt_ctxt['in'].hash,
                                tstmp,
                            )
                            ret(SimpleFormat.FILE, fn)
                        except FormatError:
                            flt_ctxt.ctxt_svc_output("dumping failed",
                                                     base='error', urgent=True)
                        else:
                            flt_ctxt.ctxt_svc_output("|subheader:dump:|"
                                                     " |highlight:{0}|"
                                                     .format(fn))
                    continue
            # output time!  (INFILTER terminal listed twice in io_chain)
            with cmd_ctxt.prevented_taint():
                io_decl = SimpleFormat.io_decl_specials(io_decl, 0, magic_fds,
                                                        cmd_ctxt['__filters__'])
            log.debug("Run `{0}' filter with `{1}' io decl. as TERMINAL"
                      .format(flt.__class__.name, io_decl))
            # store output somewhere, which even can be useful (use as a lib)
            passout['passout'] = flt_ctxt['out'](*io_decl)
            if passout is unused and io_decl[0] == SimpleFormat.FILE:
                flt_ctxt.ctxt_svc_output("|subheader:output:| |highlight:{0}|"
                                         .format(passout['passout']))

        # close "magic" fds
        map(lambda (k, f): k in native_fds or f.close(), magic_fds.iteritems())
        return EC.EXIT_SUCCESS  # XXX some better decision?

    def __call__(self, opts, args=None, cmd_ctxt=None):
        """Proceed the command"""
        ec = EC.EXIT_SUCCESS
        maxl = len(sorted(self._filters, key=len)[-1])
        color = dict(auto=None, never=False, always=True)[
            getattr(opts, 'color', 'auto')
        ]
        cmd_ctxt = cmd_ctxt or CommandContext({
            'filter_chain_analysis': self.filter_chain_analysis,
            'filter_noop':           getattr(opts, 'noop', ()),
            'filter_dump':           getattr(opts, 'dump', ()),
            'system':                getattr(opts, 'sys', ''),
            'system_extra':          filter(len, getattr(opts, 'dist', '')
                                                 .split(',')),
            'svc_output':            FancyOutput(f=stderr,
                                                 quiet=getattr(opts, 'quiet',
                                                               False),
                                                 prefix=("|header:[{{0:{0}}}]| "
                                                         .format(maxl)),
                                                 color=color,
                                     ),
            'color':                color,
        }, bypass=True)
        cmd_ctxt.ensure_filters(self._filters.itervalues())
        kwargs = {}
        # desugaring, which is useful mainly if non-contiguous sequence
        # of value-based options need to be specified
        args = [None if not a else a for a in args[0].split('::')] + args[1:] \
               if args else []
        args.reverse()  # we will be poping from the end
        for v in self._fnc_defaults_varnames[1]:
            default = self._fnc_defaults_raw.get(v, None)
            opt = getattr(opts, v, default)
            if isinstance(opt, basestring):
                try:
                    opt = opt.format(**cmd_ctxt['__filters__'])
                    # XXX type adjustment at least for bool?
                except (AttributeError, ValueError, KeyError):
                    # AttributeError ~ may be available later on,
                    #                  resolved in io_decl_specials
                    pass
            if isinstance(opt, MutableMapping) \
                    or not isinstance(default, basestring) \
                        and isinstance(opt, basestring) \
                    or areinstancesupto(opt, default, object, type) \
                        and opt != default:
                kwargs[v] = opt
                continue
            elif not isinstance(opt, (basestring, type(None))):
                log.info("`{0}' command: skipping attempt to pair argument"
                         " to non-string `{1}' option (specify whole option"
                         " instead)".format(self.__class__.name, v))
                continue
            try:
                cur = args.pop()
                while cur == '':  # deliberately skip (implicit) empty string
                    cur = args.pop()
                if cur is not None:  # incl. case of explicit empty string
                    kwargs[v] = cur.replace("''", "") if len(cur) == 2 else cur
                    continue
                raise IndexError  # "required arg not provided" for sugar spec
            except IndexError:
                if opt is not None:
                    continue
                raise CommandError(self, "missing ex-/implicit `{0}' value", v)
        if args:
            log.info("`{0}' command: unconsumed arguments: {1}"
                     .format(self.__class__.name, ', '.join("`" + a + "'"
                                                            for a in args)))
        log.debug("Running command `{0}';  args={1}, kwargs={2}"
                  .format(self.__class__.name, args, kwargs))
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

            (A, B, (C, D, P)), (O, P)

        when reformatted as per the only Approved Indenting Convention (TM):

            (A,
                (B),
                (C,
                    (D),
                    (P))),
            (O,
                (P))

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

            for the graph above, it would be -- following the only
            Approved Indenting Convention (TM) --, e.g.,:

                (
                    ('Aproto', 'a-in.txt'),
                    (
                        ('Bproto', 'b-out.txt'),
                        (
                            ('Dproto', 'd-out.txt'),
                            ('Pproto'),
                        ),
                    ),
                ),
                (
                    ('Oproto', 'o-in.txt'),
                )

            #which, as per point 4., can be further simplified as:

            #(('Aproto', 'a-in.txt'),
            #    ('Bproto', 'b-out.txt'), ('Dproto', 'd-out.txt'), ('Pproto')),
            #(('Oproto', 'e-in.txt'), )
        """
        def deco_fnc(fnc):
            log.debug("Command: deco for {0}"
                      .format(fnc))
            fnc_defaults, fnc_varnames, wrapped = defer_common(fnc, skip=1)
            attrs = {
                '__module__': fnc.__module__,  # original
                '__doc__': wrapped.__doc__,
                '_filter_chain': filter_chain,
                '_fnc': staticmethod(wrapped),
                '_fnc_defaults_varnames': (fnc_defaults, fnc_varnames),
                '_fnc_defaults_raw': fnc_defaults.copy(),  # un-interpolated
            }
            # optimization: shorten type() -> new() -> probe
            ret = cls.probe(fnc.__name__, (cls, ), attrs)
            return ret
        return deco_fnc


class CommandAlias(object):
    """Way to define either static or dynamic command alias"""
    __metaclass__ = commands

    def __new__(cls, flts, cmds, *args):
        ic, sys, sys_extra = (lambda i={}, s='', e='', *a: (i, s, e))(*args)
        # XXX really pass mutable cmds dict?
        use_obj = cls
        use_obj = use_obj._fnc(cmds, sys.lower(),
                               tuple(sys_extra.lower().split(',')))
        for i in xrange(1, 100):  # prevent infloop by force
            if isinstance(use_obj, basestring):
                use_obj = cmds.get(use_obj, None)
                if not isinstance(use_obj, (nonetype, Command)):
                    assert issubclass(use_obj, CommandAlias)
                    assert use_obj is not cls, "trivial infloop"
                    continue
            elif use_obj is None:
                pass
            else:
                assert issubclass(use_obj, (Command, CommandAlias))
                if use_obj in ic and ic[use_obj] in cmds:
                    use_obj = cmds[ic[use_obj]]
                else:
                    if use_obj in ic:
                        log.warning("Resolve at `{0}' command: already proved"
                                    " unresolvable(?)".format(use_obj.name))
                    name = '_' + use_obj.name
                    assert name not in cmds
                    ic[use_obj] = name
                    cmds[name] = use_obj = use_obj(flts, cmds, *args)
            assert isinstance(use_obj, (nonetype, Command)), repr(use_obj)
            return use_obj

    @classmethod
    def deco(outer_cls, decl):
        if not hasattr(decl, '__call__'):
            assert issubclass(decl, Command)
            fnc = lambda *args, **kwargs: decl
        else:
            fnc = decl
        log.debug("CommandAlias: deco for {0}".format(fnc))

        attrs = dict(
            __module__=fnc.__module__,
            _fnc=staticmethod(fnc)
        )
        # optimization: shorten type() -> new() -> probe
        ret = outer_cls.probe(fnc.__name__, (outer_cls, ), attrs)
        return ret
