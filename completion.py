# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Shell completion formatters"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import basename

from .utils import args2sgpl, bifilter, cli_undecor


class Completion(object):
    mapping = {}

    def __init__(self, prog, opts_common, opts_main, opts_nonmain):
        self._prog = prog
        self._opts_common = opts_common
        self._opts_main = opts_main
        self._opts_nonmain = opts_nonmain

    def scripts_prologue(self):
        return ''

    def handle_script(self, command):
        raise RuntimeError('subclasses ought to override this')

    def scripts_epilogue(self, handles, aliases):
        return ''

    def __call__(self, commands):
        cmds, aliases = bifilter(
            lambda (name, obj): not isinstance(obj, basestring),
            commands
        )
        handles, scripts = reduce(
            lambda (acc_handle, acc_script), (cmd_name, cmd):
                (lambda handle, script: (
                    acc_handle + [(cmd_name, handle)],
                    acc_script + [script]
                ))(*self.handle_script(cmd)),
            cmds,
            ([], [])
        )
        scripts = [self.scripts_prologue(), ] + scripts
        scripts.append(self.scripts_epilogue(handles, aliases))
        return '\n\n'.join(scripts)

    @classmethod
    def deco(basecls, which):
        def deco(cls):
            basecls.mapping[which] = cls
            return cls
        return deco

    @classmethod
    def get_completion(cls, which, *args):
        return cls.mapping[which](*args)


@Completion.deco("bash")
class BashCompletion(Completion):
    def __init__(self, prog, *args):
        prog = basename(prog)
        super(BashCompletion, self).__init__(prog, *args)
        self._name = cli_undecor(prog)

    @staticmethod
    def _namespaced_identifier(namespace, name=None):
        return '_'.join(filter(lambda x: x is not None, ('', namespace, name)))

    @staticmethod
    def _format_function(name, bodylines):
        bodylines = args2sgpl(bodylines)
        return ("{0}() {{\n\t{1}\n}}"
                .format(name, '\n\t'.join(bodylines).rstrip('\t')))

    @staticmethod
    def scripts_prologue():
        return """\
# bash completion start
# add me to ~/.profile persistently or eval on-the-fly in bash"""

    def handle_script(self, cmd):
        clsname = cmd.__class__.__name__
        handle = self._namespaced_identifier(self._name, clsname)
        _, opts = cmd.parser_desc_opts
        main = """\
local opts="{0}"

[[ "$1" =~ -.* ]] && compgen -W "${{opts}}" -- $1"""\
        .format(
            ' '.join(reduce(lambda a, b: a + list(b[0]), opts, []))
        ).splitlines()

        handle = cli_undecor(handle)
        return handle, self._format_function(handle, main)

    def scripts_epilogue(self, handles, aliases):
        handle = self._namespaced_identifier(self._name)
        opts_common, opts_main, opts_nonmain = tuple(
            ' '.join(reduce(lambda a, b: a + list(b[0]), o, []))
            for o in (self._opts_common, self._opts_main, self._opts_nonmain)
        )
        alias_case = '    ' + '\n    '.join(
            '{0}) cur="{1}";;'.format(alias, to) for alias, to in aliases
        )
        # usage of self._name: see self._namespaced_identifier
        main = \
r"""local commands="{1}"
local opts_common="{2}"
local opts_main="{3}"
local opts_nonmain="{4}"

local cur fnc i=${{COMP_CWORD}}
while true; do
    test ${{i}} -eq 0 && break || let i-=1
    cur=${{COMP_WORDS[${{i}}]}}
    [[ "${{cur}}" =~ ^-.* ]] && continue
    # handle aliases
    case ${{cur}} in
{5}
    esac
    fnc=_{0}_${{cur/-/_}}
    declare -f ${{fnc}} >/dev/null && COMPREPLY+=( $(${{fnc}} $2) )
    [[ "$2" =~ ^-.* ]] \
     && COMPREPLY+=( $(compgen -W "${{opts_common}} ${{opts_nonmain}}" -- $2) )
    return
done

case "$2" in
-*) COMPREPLY=( $(compgen -W "${{opts_common}} ${{opts_main}}" -- $2) );;
*)  COMPREPLY=( $(compgen -W "${{commands}}" -- $2) );;
esac""" .format(
            self._name, ' '.join(a for a, _ in (aliases + handles)),
            opts_common, opts_main, opts_nonmain, alias_case
        ).splitlines()
        epilogue = "complete -o default -F {0} {1}".format(handle, self._prog)
        return '\n\n'.join([self._format_function(handle, main), epilogue])
