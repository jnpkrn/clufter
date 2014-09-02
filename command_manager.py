# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from textwrap import wrap

from .command import commands, CommandAlias
from .error import ClufterError, ClufterPlainError, \
                   EC
from .plugin_registry import PluginManager
from .utils_func import bifilter
from .utils_prog import make_options, set_logging

log = logging.getLogger(__name__)


class CommandManagerError(ClufterError):
    pass


class CommandNotFoundError(ClufterPlainError):
    def __init__(self, cmd):
        super(CommandNotFoundError, self).__init__("Command not found: `{0}'",
                                                   cmd)


class CommandManager(PluginManager):
    """Class responsible for commands routing to filters or other actions"""
    _default_registry = commands
    _implicit = None

    def _init_handle_plugins(self, commands, flt_mgr, *args):
        log.debug("Commands before resolving: {0}".format(commands))
        self._commands = self._resolve(flt_mgr.filters, commands, *args)

    def __iter__(self):
        return self._commands.itervalues()

    @classmethod
    def implicit(cls, *args):
        """Ad-hoc simply-cached construction of "implicit" manager's chain"""
        if cls._implicit and not args:
            implicit = cls._implicit
        else:
            from .filter_manager import FilterManager
            from .format_manager import FormatManager
            implicit = cls(FilterManager(FormatManager()), *args)
            if not args:
                cls._implicit = implicit
        return implicit

    @staticmethod
    def _resolve(filters, commands, system='', system_extra=''):
        # name -> (cmd obj if not alias or resolvable name)
        aliases = []
        inverse_commands = dict((b, a) for a, b in commands.iteritems())

        # first, resolve end-use commands
        for cmd_name, cmd_cls in commands.items():
            if issubclass(cmd_cls, CommandAlias):
                aliases.append(cmd_name)
                continue
            ret = cmd_cls(filters)
            if ret is not None:
                commands[cmd_name] = ret
            else:
                commands.pop(cmd_name)

        # only then resolve the command aliases, track a string identifying
        # end-use command in `commands`
        for cmd_name in aliases:
            alias = commands[cmd_name]
            if not isinstance(alias, basestring):
                # not resolved yet
                assert issubclass(alias, CommandAlias)
                resolved = alias(filters, commands, inverse_commands,
                                 system, system_extra)
                resolved_cls = type(resolved)
                if resolved_cls not in inverse_commands:
                    if resolved is not None:
                        log.warning("Resolve at `{0}' alias: target unknown"
                                    .format(cmd_name))
                    commands.pop(cmd_name)
                else:
                    commands[cmd_name] = inverse_commands[resolved_cls]

        return commands

    @property
    def commands(self):
        return self._commands.copy()

    def completion(self, completion):
        return completion(self._commands.iteritems())

    def __call__(self, parser, args=None):
        """Follow up of the entry point, facade to particular commands"""
        ec = EC.EXIT_SUCCESS
        values = parser.values
        try:
            canonical_cmd = command = cmd = getattr(values, 'help', None) \
                                            or args[0]
            while isinstance(command, basestring):
                canonical_cmd = command
                command = self._commands.get(command, None)
            if not command:
                raise CommandNotFoundError(cmd)

            parser.description, options = command.parser_desc_opts
            parser.option_groups[0].add_options(make_options(options))

            args = ['--help'] if values.help else args[1:]
            parser.defaults.update(values.__dict__)  # from global options
            opts, args = parser.parse_args(args)
            if opts.help:
                usage = ('\n' + len('Usage: ') * ' ').join(map(
                    lambda c:
                        "%prog [<global option> ...] {0} [<cmd option ...>]"
                        .format(c),
                    sorted(set([cmd, canonical_cmd]),
                           key=lambda i: int(i == canonical_cmd))
                ))
                print parser.format_customized_help(usage=usage)
                return ec

            set_logging(opts)
            log.debug("Running command `{0}';  opts={1}, args={2}"
                      .format(cmd, opts.__dict__, args))
            ec = command(opts, args)
        except ClufterError as e:
            ec = EC.EXIT_FAILURE
            print e
            if isinstance(e, CommandNotFoundError):
                print "\n" + self.pretty_cmds()
        #except Exception as e:
        #    print "OOPS: underlying unexpected exception:\n{0}".format(e)
        #    ec = EC.EXIT_FAILURE
        return ec

    def pretty_cmds(self, text_width=76, linesep_width=1,
                    ind=' ', itemsep='\n', secsep='\n',
                    cmds_intro='Commands:', aliases_intro='Aliases:',
                    refer_str='alias for {0}'):
        """Return string containing formatted list of commands (name + desc)"""
        cmds_aliases = [
            ([(name, refer_str.format(obj) if i else
                     obj.__doc__.splitlines()[0]) for name, obj in sorted(cat)],
              max(tuple(len(name) for name, _ in cat)) if cat else 0)
            for i, cat in enumerate(
                bifilter(lambda (name, obj): not isinstance(obj, basestring),
                         self._commands.iteritems())
            )
        ]
        width = max(i[1] for i in cmds_aliases) + linesep_width
        desc_indent = ind + (width * ' ')
        text_width -= len(desc_indent)
        text_width = max(text_width, 20)
        return secsep.join(
            itemsep.join([header] + [
                '{0}{1:{width}}{2}'.format(
                    ind, name, '\n'.join(
                        wrap(desc,
                             width=text_width, subsequent_indent=desc_indent)
                    ), width=width
                ) for name, desc in i[0]
            ]) for header, i in zip((cmds_intro, aliases_intro), cmds_aliases)
        )
