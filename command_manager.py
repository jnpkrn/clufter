# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .command import commands
from .error import ClufterError, ClufterPlainError, \
                   EC
from .plugin_registry import PluginManager
from .utils import apply_preserving_depth, \
                   apply_aggregation_preserving_depth, \
                   apply_intercalate

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

    def _init_handle_plugins(self, commands, flt_mgr):
        log.debug("Commands before resolving: {0}"
                  .format(commands))
        self._commands = self._resolve(flt_mgr.filters, commands)

    @staticmethod
    def _resolve(filters, commands):
        for cmd_name, cmd_cls in commands.items():
            res_input = cmd_cls.filter_chain
            res_output = apply_preserving_depth(filters.get)(res_input)
            if apply_aggregation_preserving_depth(all)(res_output):
                log.debug("resolve at `{0}' command: `{1}' -> {2}"
                          .format(cmd_name, repr(res_input), repr(res_output)))
                commands[cmd_name] = cmd_cls(*res_output)
                continue
            # drop the command if cannot resolve any of the filters
            res_input = apply_intercalate(res_input)
            log.debug("cmd_name {0}".format(res_input))
            map(lambda (i, x): log.warning("Resolve at `{0}' command:"
                                           " `{1}' (#{2}) filter fail"
                                           .format(cmd_name, res_input[i], i)),
                filter(lambda (i, x): not(x),
                       enumerate(apply_intercalate(res_output))))
            commands.pop(cmd_name)
        return commands

    @property
    def commands(self):
        return self._commands.copy()

    def __call__(self, parser, args=None):
        """Follow up of the entry point, facade to particular commands"""
        ec = EC.EXIT_SUCCESS
        values = parser.values
        try:
            cmd = getattr(values, 'help', None) or args[0]

            command = self._commands.get(cmd, None)
            if not command:
                raise CommandNotFoundError(cmd)
            canonical_cmd = command.__class__.name

            parser.description, options = command.parser_desc_opts()
            parser.option_groups[0].add_options(options)

            args = ['--help'] if values.help else args[1:]
            parser.defaults.update(values.__dict__)  # from global options
            opts, args = parser.parse_args(args)
            if opts.help:
                usage = '\n'.join(map(
                    lambda c:
                        "%prog [<global option> ...] {0} [<cmd option ...>]"
                        .format(c),
                    sorted(set([cmd, canonical_cmd]),
                           key=lambda i: int(i == canonical_cmd))
                ))
                print parser.format_customized_help(usage=usage)
                return ec
            logging.getLogger().setLevel(opts.loglevel)
            log.debug("Running command `{0}';  opts={1}, args={2}"
                      .format(cmd, opts.__dict__, args))
            ec = command(opts, args)
        except ClufterError as e:
            ec = EC.EXIT_FAILURE
            print e
            if isinstance(e, CommandNotFoundError):
                print "\nSupported commands:\n" + self.cmds()
        #except Exception as e:
        #    print "OOPS: underlying unexpected exception:\n{0}".format(e)
        #    ec = EC.EXIT_FAILURE
        return ec

    def cmds(self, ind='', sep='\n'):
        """Return string containing formatted list of commands (name + desc)"""
        return '\n'.join(map(
            lambda (cname, ccls):
                '{0}{1!s:12}{2}'.format(ind, cname,
                                        ccls.__doc__.splitlines()[0]),
            self._commands.iteritems()
        ))
