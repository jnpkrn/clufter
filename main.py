# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Machinery entry point"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from optparse import OptionParser, \
                     OptionGroup, \
                     IndentedHelpFormatter
from os.path import basename, realpath
from platform import system, linux_distribution
try:
    from platform import _supported_dists
except ImportError:
    _supported_dists = ()
_supported_dists += ('fedora', 'redhat')  # actively used in the templates
from sys import version

from . import version_parts, version_text, description_text
from .command_manager import CommandManager
from .completion import Completion
from .error import EC
from .facts import aliases_dist
from .utils import args2sgpl, head_tail, identity
from .utils_prog import ExpertOption, make_options, set_logging, which

try:
    from .defaults import REPORT_BUGS
except ImportError:
    report_bugs = ()
else:
    report_bugs = ("Report bugs to <{0}>.".format(REPORT_BUGS), )


_system = system().lower()
_system_extra = linux_distribution(full_distribution_name=0) \
                if _system == 'linux' else ()


def parser_callback_help(option, opt_str, value, parser, arg=False, full=False):
    """Makes 'help' option accept 'optional option arguments'"""
    if arg:
        rargs, val = parser.rargs, ''
        if rargs and not rargs[0].startswith('-'):
            val = rargs[0]
            del rargs[:1]
    else:
        val = True
    setattr(parser.values, 'help', val)
    setattr(parser.values, 'help_full', full)


def parser_callback_sys(option, opt_str, value, parser, *args, **kwargs):
    setattr(parser.values, option.dest, value.lower())


def parser_callback_dist(option, opt_str, value, parser, *args, **kwargs):
    orig_distro, orig_version = head_tail(value.split(',', 1))
    distro = orig_distro
    for fn in (lambda x: x.lower(), lambda x: aliases_dist.get(x, x), identity):
        if distro in _supported_dists:
            if distro != orig_distro:
                parser.values._deferred_log = dl = getattr(parser.values,
                                                           '_deferred_log', [])
                dl.append((logging.INFO, "Distro `{0}' recognized as `{1}'"
                                         .format(orig_distro, distro)))
            break
        distro = fn(distro)
    else:
        parser.values._deferred_log = dl = getattr(parser.values,
                                                   '_deferred_log', [])
        dl.append((logging.WARNING, "Unrecognized distro `{0}' may lead to"
                                    " unexpected results".format(orig_distro)))
    setattr(parser.values, option.dest, ','.join(args2sgpl(distro,
                                                           *orig_version)))


opts_common = (
    (('--sys', ), dict(
        type='string',  # for dest -> default
        action='callback',
        callback=parser_callback_sys,
        default=_system,
        expert=True,
        help="override autodetected system [%default]"
    )),
    (('--dist', ), dict(
        type='string',  # for dest -> default
        action='callback',
        callback=parser_callback_dist,
        default=','.join(_system_extra),
        help="override autodetected target distro (for SYS ~ linux) [%default]"
    )),
    (('-q', '--quiet', ), dict(
        action='store_true',
        help="refrain from unnecesary messages (usually on stderr)"
    )),
    (('--color', ), dict(
        metavar="[WHEN]",
        action='store',
        dest='color',
        default='auto',
        type='choice',
        choices=('auto', 'never', 'always'),
        help="colorize messages if available [%default out of %choices]"
    )),
    (('-d', '--debug'), dict(
        action='store_const',
        dest='loglevel',
        const='DEBUG',
        help="shortcut for --loglevel=DEBUG"
    )),
    (('--logfile', ), dict(
        metavar="FILE",
        action='store',
        dest='logfile',
        default='',
        help="specify log file (instead of stderr)"
    )),
    (('--loglevel', ), dict(
        metavar="LEVEL",
        action='store',
        dest='loglevel',
        default=logging.getLevelName(logging.WARNING),
        type='choice',
        choices=map(logging.getLevelName,
                    xrange(logging.NOTSET, logging.CRITICAL + 1,
                           logging.DEBUG - logging.NOTSET)),
        help="specify log level [%default out of %choices]"
    )),
    # TODO other logging related stuff (if any)
)

opts_main = (
    (('-h', '--help'), dict(
        metavar="[CMD]",
        type='string',
        nargs=0,  # <- we take one if suitable
        action='callback',
        callback=lambda *args: parser_callback_help(*args, arg=True),
        help="show help message (can be command-specific) and exit"
    )),
    (('-H', '--help-full'), dict(
        metavar="[CMD]",
        type='string',
        nargs=0,  # <- we take one if suitable
        action='callback',
        callback=lambda *args: parser_callback_help(*args, arg=True, full=True),
        help="full help message (can be command-specific) and exit"
    )),
    (('-l', '--list'), dict(
        action='store_true',
        help="list commands and exit"
    )),
    (('-v', '--version'), dict(
        action='store_true',
        help="show version details and exit"
    )),
    (('-e', '--ext'), dict(
        action='append',
        dest='ext_user',
        expert=True,
        help="specify dir/s (as PATH/multiplied) scanned for plugins"
    )),
    (('-s', '--skip-ext'), dict(
        action='store_true',
        dest='skip_ext',
        help="do not use standard external plugins"
    )),
    (('--completion-bash', ), dict(
        action='store_const',
        dest='completion', const='bash',
        help="generate bash completion and exit"
    )),
)

opts_nonmain = (
    (('-h', '--help'), dict(
        action='callback',
        callback=parser_callback_help,
        help="show help message and exit"
    )),
    (('-H', '--help-full'), dict(
        action='callback',
        callback=lambda *args: parser_callback_help(*args, full=True),
        help="full help message and exit"
    )),
)


class SharedHelpFormatter(IndentedHelpFormatter):
    """IndentedHelpFormatter to expand choices along defaults"""
    choices_tag = "%choices"

    def expand_default(self, option):
        ret = IndentedHelpFormatter.expand_default(self, option)
        if isinstance(option, ExpertOption):
            ret = "(Advanced) " + ret
        return ret.replace(self.choices_tag, ', '.join(option.choices or []))


class SharedHelpFormatterNonExpert(SharedHelpFormatter):
    """SharedHelpFormatter to filter out expert options"""
    def format_option(self, option):
        if not isinstance(option, ExpertOption):
            ret = SharedHelpFormatter.format_option(self, option)
        else:
            ret = ''
        return ret


class SharedOptionParser(OptionParser):
    """OptionParser with a dynamic on-demand help screen customization."""

    formatter_nonexpert = SharedHelpFormatterNonExpert()
    formatter_expert = SharedHelpFormatter()

    # overridden methods

    def __init__(self, **kwargs):
        # a bit awkward, but in place as a sort of memoizing
        if 'formatter' not in kwargs:
            kwargs['formatter'] = self.formatter_nonexpert
        OptionParser.__init__(self, **kwargs)
        self.formatter_expert.set_parser(self)  # ensure %default expansion
        self.description_raw = ''

    def format_description(self, formatter):
        # cf. http://bugs.python.org/issue4318
        return '\n'.join(formatter.format_description(l)
                         for l in self.get_description().split('\n\n')) \
               + (self.description_raw and '\n' + self.description_raw + '\n')

    def format_epilog(self, formatter):
        return ''.join(formatter.format_epilog(l)
                       for l in self.epilog.split('\n'))

    # custom methods

    def format_customized_help(self, **kwargs):
        for k in ('usage', 'description', 'description_raw', 'epilog'):
            v = kwargs.pop(k, None)
            if v:
                setattr(self, k, v)
        help_full = getattr(self.values, 'help_full', None)
        if help_full in (True, False):
            self.help_full(help_full)
        return self.format_help(**kwargs)

    def add_option_group_by_args(self, *args, **kwargs):
        option_list = kwargs.pop('option_list', None)
        group = OptionGroup(self, *args, **kwargs)
        if option_list:
            group.add_options(option_list)
        self.add_option_group(group)

    def help_full(self, expert):
        assert self.formatter in (self.formatter_nonexpert,
                                  self.formatter_expert), "explicit formatter"
        self.formatter = (self.formatter_expert if expert else
                          self.formatter_nonexpert)


def run(argv=None, *args):
    """Entry point"""
    # re option parser: only one instance is used, modified along
    ec = EC.EXIT_SUCCESS
    argv = list(argv) + list(args) if argv else list(args)
    prog, argv = (argv[0], argv[1:]) if argv else ('<script>', [])
    prog_simple = basename(prog)
    prog_full = prog if prog != prog_simple else which(prog_simple, '.', '')
    prog_real = basename(realpath(prog_full))

    parser = SharedOptionParser(prog=prog_simple, add_help_option=False)
    parser.disable_interspersed_args()  # enforce ordering as per "usage"
    parser.add_option_group_by_args(
        "Standalone global options", "These take precedence over any command.",
        option_list=make_options(opts_main)
    )
    parser.add_option_group_by_args(
        "Common options",
        "Either in global (before <cmd>) or command scope (after <cmd>).",
        option_list=make_options(opts_common)
    )

    opts, args = parser.parse_args(argv)
    if prog_simple == prog_real and opts.help is None:
        # options that return/exit + don't need plugin resolutions (not help)
        if opts.version:
            loglevel = logging.getLevelName(opts.loglevel)
            msg = version_parts
            if loglevel <= logging.INFO:
                msg += ('', "Python runtime:", version)
            print version_text(*msg)
            return ec

    logging.basicConfig()
    try:
        # only 2.7+ (despite not documented this way)
        logging.captureWarnings(True)
    except AttributeError:
        pass
    set_logging(opts)
    log = logging.getLogger(__name__)
    map(lambda args: log.log(*args), getattr(opts, '_deferred_log', ()))

    cm = CommandManager.init_lookup(ext_plugins=not opts.skip_ext,
                                    ext_plugins_user=opts.ext_user,
                                    system=opts.sys, system_extra=opts.dist)
    if prog_simple == prog_real and not opts.help \
       and (opts.list or opts.completion or not args):
        cmds = cm.pretty_cmds(ind=' ' * parser.formatter.indent_increment,
                              linesep_width=2,
                              cmds_intro="Commands"
                                         " (as available, but stable)",
                              aliases_intro="Aliases thereof"
                                            " (environment-specific):",
                              ellip_yes='; built-in only' + (
                                         ' required:' if opts.skip_ext else
                                        ', use --list to get all:'),
                              ellip=opts.skip_ext or not opts.list)
        if opts.list:
            print cmds
        elif opts.completion:
            c = Completion.get_completion(opts.completion, prog,
                                          opts_common, opts_main, opts_nonmain)
            print c(cm.plugins.iteritems())
        else:
            print parser.format_customized_help(
                usage="%prog [<global option> ...] [<cmd> [<cmd option ...>]]",
                description=description_text(width=0),
                description_raw=cmds,
                epilog='\n'.join(args2sgpl(
                    "To get help for given command, just precede or follow"
                    " it with `--help'.",
                    *report_bugs
                ))
            )
        return ec
    elif prog_simple != prog_real:
        args = [prog_simple] + argv

    # prepare option parser to be reused by sub-commands
    parser.enable_interspersed_args()
    modify_group = parser.get_option_group(opts_main[0][0][0])
    map(parser.remove_option, map(lambda x: x[0][0], opts_main))
    modify_group.set_title("Command options")
    modify_group.set_description(None)
    parser.add_options(make_options(opts_nonmain))
    parser.epilog = '\n'.join(args2sgpl(
        "Arguments to value-based `command options' can go without labels"
        " when the order wrt. parsing logic respected;"
        " skipping those backed by default values otherwise requiring"
        " specification then allowed by syntactic sugar: all can be passed"
        " as a single, first, ::-delimited argument;"
        " magic files: `-', `@DIGIT+'. `{{formula}}' in output file spec:"
        " input-backed (e.g. hash) substitution recipe."
        "  All available commands listed as `{0} --list'."
        .format(prog_simple),
        *report_bugs
    ))
    #try:
    # note that the parser carries opts and "Common options" group
    ec = cm(parser, args)
    #except Exception as e:
    #    print "FATAL: Unhandled exception: {0}".format(e)
    #    ex = EC.EXIT_FAILURE
    return ec
