# -*- coding: UTF-8 -*-
version = '0.1'
copyright = """\
Copyright 2014 Red Hat, Inc.
Licensed under GPLv2
""".rstrip()
author = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

metadata = (version, copyright, author)

description = """\
Tool to perform various transformations on cluster configuration formats.

Primarily aimed at (CMAN, rgmanager) -> (Corosync, Pacemaker) cluster
stacks configuration conversion (following RHEL trend), the tool,
however, offers more uses further extensible within the arranged
commands-filters-formats plugin framework.
"""
#Native plugins allows also for obfuscation of sensitive data within
#cluster configuration of supported cluster stacks, and other
#convenient actions.


def version_text(package=None, sep='\n'):
    if package is None:
        from os.path import basename, dirname
        package = basename(dirname(__file__))
    return (package + ' ' + sep.join(metadata)
            .replace(' \n', '\n')
            .replace(' @at@ ', '@')
            .replace(' .dot. ', '.')
            .replace('@Red Hat.', '@redhat.'))


def description_text(width=70):
    if not width:
        return description
    from textwrap import fill
    desc = map(lambda p: p.replace('\n', ' '), description.split('\n\n'))
    return '\n\n'.join(map(lambda p: fill(p, width), desc)) + '\n'
