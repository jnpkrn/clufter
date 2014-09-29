# -*- coding: UTF-8 -*-
version = '0.1.4-alpha'
license = 'GPLv2+'
copyright = """\
Copyright 2014 Red Hat, Inc.
Licensed under {0}
""".format(license).rstrip()
# XXX eventually there should be precise plugin authorship tracking
author = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com> and plugin authors"

metadata = (version, copyright, author)

description = """\
Tool/library for transforming/analyzing cluster configuration formats

Primarily aimed at (CMAN, rgmanager) -> (Corosync, Pacemaker) cluster
stacks configuration conversion (following RHEL trend), but the package
has a more universal use as commands-filters-formats plugin framework.
"""
#Native plugins allows also for obfuscation of sensitive data within
#cluster configuration of supported cluster stacks, and other
#convenient actions.

pkg_name = globals().get('ROOT')

_deobfuscate_email = (lambda what: what.replace(' @at@ ', '@')
                                       .replace(' .dot. ', '.')
                                       .replace('@Red Hat.', '@redhat.'))


def package_name():
    global pkg_name
    if pkg_name is None:
        from os.path import abspath, basename, dirname, realpath
        pkg_name = basename(dirname(realpath(abspath(__file__))))
    return pkg_name


def author_text(justname=None, first=False):
    if justname is not None or first:
        ret = ''
        authors = author.split(', ')
        first = first or len(authors) == 1
        for a in authors:
            name, rest = a.split('<', 1)
            email, rest = rest.split('>', 1)
            name, email, rest = map(str.strip, (name, email, rest))
            if justname:
                ret += ('' if first else ', ') + ' '.join((name, rest))
            else:
                ret += ('' if first else ', ') + _deobfuscate_email(email)
            if first:
                break
        return ret
    return _deobfuscate_email(author).lstrip('<').rstrip('>')


def copyright_text(justcopyright=None):
    if justcopyright is not None:
        c, licensed = copyright.split('\n', 1).rstrip()
        return c if justcopyright else licensed
    return copyright


def description_text(width=76, justhead=None):
    desc = description
    if justhead is False:
        desc = desc.split('\n', 2)[2]
    if not width or justhead is True:
        if justhead is True:
            desc = desc.split('\n', 1)[0]
            assert len(desc) <= (width or 1000)
    else:
        from textwrap import fill
        desc = map(lambda p: p.replace('\n', ' '), desc.split('\n\n'))
        desc = '\n\n'.join(map(lambda p: fill(p, width), desc))  #+ '\n'
    return desc


def version_text(name=pkg_name, sep='\n'):
    if name is None:
        name = package_name()
    return (name + ' '
            + _deobfuscate_email(sep.join(metadata).replace(' \n', '\n')))
