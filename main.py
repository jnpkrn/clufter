# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Machinery entry point"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from optparse import OptionParser, \
                     OptionGroup, \
                     IndentedHelpFormatter
from os.path import basename
from platform import system, linux_distribution
from sys import version

from . import version_text, description_text
from .command_manager import CommandManager
from .completion import Completion
from .error import EC
from .format_manager import FormatManager
from .filter_manager import FilterManager
from .utils_prog import make_options, set_logging


_system = system()
_system_extra = linux_distribution(full_distribution_name=0) \
                if _system == 'Linux' else ()


def parser_callback_help(option, opt_str, value, parser):
    """Makes 'help' option accept 'optional option arguments'"""
    rargs, val = parser.rargs, ''
    if rargs and not rargs[0].startswith('-'):
        val = rargs[0]
        del rargs[:1]
    setattr(parser.values, 'help', val)

opts_common = (
    (('-q', '--quiet', ), dict(
        action='store_true',
        help="refrain from unnecesary messages (usually on stderr)"
    )),
    (('--loglevel', ), dict(
        action='store',
        dest='loglevel',
        default=logging.getLevelName(logging.WARNING),
        type="choice",
        choices=map(logging.getLevelName,
                    xrange(logging.NOTSET, logging.CRITICAL + 1,
                           logging.DEBUG - logging.NOTSET)),
        help="set loglevel to specified value [%default out of %choices]"
    )),
    (('--logfile', ), dict(
        action='store',
        dest='logfile',
        default='',
        help="log to specified file instead of stderr"
    )),
    # TODO other logging related stuff (file, ...)
    (('-d', '--debug'), dict(
        action='store_const',
        dest='loglevel',
        const='DEBUG',
        help="shortcut for --loglevel=DEBUG"
    )),
    (('--sys', ), dict(
        action='store',
        default=_system,
        help="override autodetected system [%default]"
    )),
    (('--dist', ), dict(
        action='store',
        default=','.join(_system_extra),
        help="override autodetected distro if sys==Linux [%default]"
    )),
)

opts_main = (
    (('-h', '--help'), dict(
        metavar="[CMD]",
        type='string',
        nargs=0,  # <- we take one if suitable
        action='callback',
        callback=parser_callback_help,
        help="show this help message (global or command-specific) and exit"
    )),
    (('-v', '--version'), dict(
        action='store_true',
        help="show version details and exit"
    )),
    (('-l', '--list'), dict(
        action='store_true',
        help="list commands and exit"
    )),
    (('--completion-bash', ), dict(
        action='store_const',
        dest='completion', const='bash',
        help="generate bash completion and exit"
    )),
)

opts_nonmain = (
    (('-h', '--help'), dict(
        action='store_true',
        help="show this help message and exit"
    )),
)


class SharedHelpFormatter(IndentedHelpFormatter):
    """IndentedHelpFormatter to expand choices along defaults"""
    choices_tag = "%choices"

    def expand_default(self, option):
        ret = IndentedHelpFormatter.expand_default(self, option)
        return ret.replace(self.choices_tag, ', '.join(option.choices or []))


class SharedOptionParser(OptionParser):
    """OptionParser with a dynamic on-demand help screen customization."""

    # overridden methods

    def __init__(self, **kwargs):
        if not 'formatter' in kwargs:
            kwargs['formatter'] = SharedHelpFormatter()
        OptionParser.__init__(self, **kwargs)
        self.description_raw = ''

    def format_description(self, formatter):
        # cf. http://bugs.python.org/issue4318
        return '\n'.join(formatter.format_description(l)
                         for l in self.get_description().split('\n\n')) \
               + (self.description_raw and '\n' + self.description_raw + '\n')

    # custom methods

    def format_customized_help(self, **kwargs):
        for k in ('usage', 'description', 'description_raw', 'epilog'):
            v = kwargs.pop(k, None)
            if v:
                setattr(self, k, v)
        return self.format_help(**kwargs)

    def add_option_group_by_args(self, *args, **kwargs):
        option_list = kwargs.pop('option_list', None)
        group = OptionGroup(self, *args, **kwargs)
        if option_list:
            group.add_options(option_list)
        self.add_option_group(group)


def run(argv=None, *args):
    """Entry point"""
    # re option parser: only one instance is used, modified along
    ec = EC.EXIT_SUCCESS
    argv = list(argv) + list(args) if argv else list(args)
    prog, args = (argv[0], argv[1:]) if argv else ('<script>', [])
    prog_simple = basename(prog)

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

    opts, args = parser.parse_args(args)
    if opts.help is None:
        # options that return/exit + don't need plugin resolutions (not help)
        if opts.version:
            print '\n'.join((version_text(), '-- \nPython runtime:', version))
            return ec

    logging.basicConfig()
    try:
        # only 2.7+ (despite not documented this way)
        logging.captureWarnings(True)
    except AttributeError:
        pass
    set_logging(opts)

    cm = CommandManager(FilterManager(FormatManager()), opts.sys, opts.dist)
    if not opts.help and (opts.list or opts.completion or not args):
        cmds = cm.pretty_cmds(ind=' ' * parser.formatter.indent_increment,
                              linesep_width=2,
                              cmds_intro="Commands"
                                         " (as available, but stable):",
                              aliases_intro="Aliases thereof"
                                            " (environment-specific):")
        if opts.list:
            print cmds
        elif opts.completion:
            print cm.completion(
                Completion.get_completion(opts.completion,
                                          prog,
                                          opts_common, opts_main, opts_nonmain)
            )
        else:
            print parser.format_customized_help(
                usage="%prog [<global option> ...] [<cmd> [<cmd option ...>]]",
                description=description_text(width=0),
                description_raw=cmds,
                epilog=("To get help for given command,"
                        " just precede or follow it with `--help'.")
            )
        return ec

    # prepare option parser to be reused by sub-commands
    parser.enable_interspersed_args()
    modify_group = parser.get_option_group(opts_main[0][0][0])
    map(parser.remove_option, map(lambda x: x[0][0], opts_main))
    modify_group.set_title("Command options")
    modify_group.set_description(None)
    modify_group.add_options(make_options(opts_nonmain))
    parser.epilog = ("Arguments to value-based `command options' can go"
                     " without labels when the order wrt. parsing logic"
                     " respected;"
                     " skipping those backed by default values otherwise"
                     " requiring specification then allowed by syntactic"
                     " sugar: all can be passed as a single, first,"
                     " ::-delimited argument;"
                     " magic files: `-', `@DIGIT+'."
                     "  All available commands listed as `{0} --list'."
                     .format(prog_simple))
    #try:
    # note that the parser carries opts and "Common options" group
    ec = cm(parser, args)
    #except Exception as e:
    #    print "FATAL: Unhandled exception: {0}".format(e)
    #    ex = EC.EXIT_FAILURE
    return ec
