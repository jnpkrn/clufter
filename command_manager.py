# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command manager"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from logging import getLogger
from os.path import abspath, dirname, join
from textwrap import wrap
from sys import modules

from .command import commands, CommandAlias
from .error import ClufterError, ClufterPlainError, \
                   EC
from .filter_manager import FilterManager
from .plugin_registry import PluginManager
from .utils import filterdict_keep
from .utils_2to3 import basestring, iter_items, iter_values
from .utils_func import apply_intercalate, bifilter_unpack
from .utils_prog import make_options, set_logging

log = getLogger(__name__)


class CommandManagerError(ClufterError):
    pass


class CommandNotFoundError(ClufterPlainError):
    def __init__(self, cmd):
        super(CommandNotFoundError, self).__init__("Command not found: `{0}'",
                                                   cmd)


class CommandManager(PluginManager):
    """Class responsible for commands routing to filters or other actions"""
    _default_registry = commands

    @classmethod
    def _init_plugins(cls, commands, flt_mgr=None, *args, **kwargs):
        log.debug("Commands before resolving: {0}".format(commands))
        if flt_mgr is None:
            flts = set()
            for cmd in iter_values(commands):
                for flt in apply_intercalate(getattr(cmd, 'filter_chain', ())):
                    flts.add(flt)
            flt_mgr = FilterManager.init_lookup(flts, **kwargs)
        return cls._resolve(flt_mgr.filters, commands, *args,
                            **filterdict_keep(kwargs, 'system', 'system_extra'))

    @staticmethod
    def _resolve(filters, commands, system='', system_extra=''):
        # name -> (cmd obj if not alias or resolvable name)
        aliases = []
        inverse_commands = dict((b, a) for a, b in iter_items(commands))

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
        return self._plugins

    def __call__(self, parser, args=None):
        """Follow up of the entry point, facade to particular commands"""
        ec = EC.EXIT_SUCCESS
        values = parser.values
        try:
            canonical_cmd = command = cmd = getattr(values, 'help', None) \
                                            or args[0]
            while isinstance(command, basestring):
                canonical_cmd = command
                command = self._plugins.get(command, None)
            if not command:
                # XXX maybe it just hasn't been resolved successfully
                raise CommandNotFoundError(cmd)

            opt_group = parser.option_groups[0]
            parser.description, options = command.parser_desc_opts(opt_group)
            opt_group.add_options(make_options(options))

            args = ['--help'] if values.help else args[1:]
            parser.defaults.update(values.__dict__)  # from global options
            opts, args = parser.parse_args(args)
            if opts.help:
                sep = '\n{0:^{width}}'.format('or:', width=len('Usage: '))
                usage = sep.join(map(
                    lambda c:
                        "{0}{1} [<cmd option ...>]"
                        .format("%prog [<global option> ...] "
                                if parser.prog != c else '', c),
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

    def pretty_cmds(self, text_width=77, linesep_width=1,
                    ind='  ', itemsep='\n', secsep='\n', intmark=' *',
                    cmds_intro='Commands', aliases_intro='Aliases:',
                    ellip_yes='; only built-in ones included:',
                    ellip_no='; those without star (\'*\') are built-in:',
                    ref_str='alias for {0}', ellip=False):
        """Return string containing formatted list of commands (name + desc)"""
        pth = join(dirname(abspath(__file__)), self._registry.__name__)  # int.
        cmds_aliases = [
            ([(name, ref_str.format(obj) if i else obj.__doc__.splitlines()[0],
               i or dirname(modules[obj.__class__.__module__].__file__) == pth)
              for name, obj in sorted(cat) if obj],
              max((0, ) + tuple(len(name) for name, obj in cat
                                if obj and (not ellip or i or dirname(
                                    modules[obj.__class__.__module__].__file__
                                ) == pth)))
            )
            for i, cat in enumerate(bifilter_unpack(
                lambda name, obj: not isinstance(obj, basestring),
                iter_items(self._plugins)
            ))
        ]
        width = max(i[1] for i in cmds_aliases) + linesep_width
        desc_indent = ind + (width * ' ')
        text_width = max(text_width - len(desc_indent), 20)
        cmds_intro += ellip_yes if ellip else ellip_no
        return secsep.join(
            itemsep.join([header] + [
                '{0}{1:{width}}{2}'.format(
                    ind if internal else intmark + ind[len(intmark):],
                    name, '\n'.join(
                        wrap(desc,
                             width=text_width, subsequent_indent=desc_indent)
                    ), width=width
                ) for name, desc, internal in i[0] if not ellip or internal
            ]) for header, i in zip((cmds_intro, aliases_intro), cmds_aliases)
        )
