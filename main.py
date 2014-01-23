# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Machinery entry point"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
import re
from optparse import make_option, \
                     OptionParser, \
                     OptionGroup, \
                     IndentedHelpFormatter

from .format_manager import FormatManager
from .filter_manager import FilterManager
from .command_manager import CommandManager
from .utils import EC
from . import version_text, description_text


def parser_callback_help(option, opt_str, value, parser):
    """Makes 'help' option accept 'optional option arguments'"""
    rargs, val = parser.rargs, ''
    if rargs and not rargs[0].startswith('-'):
        val = rargs[0]
        del rargs[:1]
    setattr(parser.values, 'help', val)


opts_common = [
    make_option('--loglevel',
        action='store', dest='loglevel',
        default=logging.getLevelName(logging.WARNING),
        type="choice", choices=map(logging.getLevelName,
                                   xrange(logging.NOTSET, logging.CRITICAL+1,
                                          logging.DEBUG-logging.NOTSET)),
        help="set loglevel to specified value [%default out of %choices]"
    ),
    make_option('-d', '--debug',
        action='store_const', dest='loglevel', const='DEBUG',
        help="shortcut for --loglevel=DEBUG"
    ),
    # TODO: other logging related stuff (file, ...)
]

opts_main = [
    make_option('-h', '--help', metavar="[CMD]",
        type='string', nargs=0,  # <- we take one if suitable
        action='callback', callback=parser_callback_help,
        help="show this help message (global or command-specific) and exit"
    ),
    make_option('-v', '--version',
        action='store_true', help="show version details and exit"
    ),
    make_option('-l', '--list',
        action='store_true',
        help="list commands and exit"
    ),
    #make_option('--completion-bash', help="generate bash completion and exit")
]

opts_nonmain = [
    make_option('-h', '--help',
        action='store_true',
        help="show this help message and exit"
    )
]


class SharedHelpFormatter(IndentedHelpFormatter):
    """IndentedHelpFormatter to expand choices along defaults"""
    choices_tag = "%choices"

    def expand_default(self, option):
        ret = IndentedHelpFormatter.expand_default(self, option)
        return ret.replace(self.choices_tag, ', '.join(option.choices or []))


class SharedOptionParser(OptionParser):
    """OptionParser with a dynamic on-demand help screen customization."""

    re_description_split = re.compile(r'(?<=:)\n|\n{2}')

    # overridden methods

    def __init__(self, **kwargs):
        if not 'formatter' in kwargs:
            kwargs['formatter'] = SharedHelpFormatter()
        OptionParser.__init__(self, **kwargs)

    def format_description(self, formatter):
        # cf. http://bugs.python.org/issue4318
        return '\n'.join(
            formatter.format_description(l).replace(':\n', ':')
            for l in self.re_description_split.split(self.get_description())
        )

    # custom methods

    def format_customized_help(self, **kwargs):
        for k in ('usage', 'description', 'epilog'):
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

    parser = SharedOptionParser(prog=prog, add_help_option=False)
    parser.disable_interspersed_args()  # enforce ordering as per "usage"
    parser.add_option_group_by_args(
        "Standalone global options", "These take precedence over any command.",
        option_list=opts_main
    )
    parser.add_option_group_by_args(
        "Common options",
        "Either in global (before <cmd>) or command scope (after <cmd>).",
        option_list=opts_common
    )

    opts, args = parser.parse_args(args)
    if opts.help is None:
        # options that causes return/exit have lower priority than help
        if opts.version:
            # this is independent of plugins
            print version_text()
            return ec

    logging.basicConfig(level=opts.loglevel)  # what if not the first use?
    cm = CommandManager(FilterManager(FormatManager()))
    if not opts.help and (opts.list or not args):
        ind = ' ' * parser.formatter.indent_increment
        cmds = "Available commands (cmd):\n{0}".format(cm.cmds(ind=ind))
        if opts.list:
            print cmds
        else:
            print parser.format_customized_help(
                usage="%prog [<global option> ...] [<cmd> [<cmd option ...>]]",
                description="{0}\n{1}".format(description_text(width=0), cmds),
                epilog="To get help for given command, follow it with --help."
            )
        return ec

    # prepare option parser to be reused by sub-commands
    parser.enable_interspersed_args()
    modify_group = parser.get_option_group(opts_main[0].get_opt_string())
    map(parser.remove_option, map(lambda x: x.get_opt_string(), opts_main))
    modify_group.set_title("Command options")
    modify_group.set_description(None)
    modify_group.add_options(opts_nonmain)
    parser.epilog = ("To list all available commands, use {0} --list"
                     " (or --help)".format(prog))
    #try:
    # note that the parser carries opts and "Common options" group
    ec = cm(parser, args)
    #except Exception as e:
    #    print "FATAL: Unhandled exception: {0}".format(e)
    #    ex = EC.EXIT_FAILURE
    return ec
