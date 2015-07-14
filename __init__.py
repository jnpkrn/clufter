# -*- coding: UTF-8 -*-
version, alpha = '0.50.1', False

# https://www.python.org/dev/peps/pep-0440 + git export magic using export-subst
_git_hash = "$Format:%h$".strip('$').replace("Format:%h", "")
_git_deco = '$Format:%d$'.strip('$()').replace("Format:%d", "")
_git_deco_arr = _git_deco.split(', ')
_git_tags = [i for i in _git_deco_arr if i.startswith("tag: v")]
_git_branches = [i for i in _git_deco_arr if i not in _git_tags + ['HEAD']]
if _git_branches and not _git_branches[-1].endswith('master') or alpha:
    if alpha:  # if not alpha, it is still not a true serving release
        version += 'a'  # no dashes(?)
    if _git_hash:
        version += '+git.{0}'.format(_git_hash)
elif _git_tags:
    assert any(t.endswith(version) for t in _git_tags), "version != tag"

license = 'GPLv2+'
copyright = """\
Copyright 2015 Red Hat, Inc.
Licensed under {0}.
""".format(license).rstrip()

pkg_name = globals().get('__root__')

def package_name():
    global pkg_name
    if pkg_name is None:
        from os import readlink
        from os.path import abspath, basename, dirname, islink
        here = dirname(abspath(__file__))
        pkg_name = basename(abspath(readlink(here) if islink(here) else here))
    return pkg_name

# XXX eventually there should be precise plugin authorship tracking
author = ("Jan Pokorný <jpokorny+pkg-{0} @at@ Red Hat .dot. com>"
          " and plugin authors").format(package_name())

description = """\
Tool/library for transforming/analyzing cluster configuration formats

While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.
"""
#Native plugins allows also for obfuscation of sensitive data within
#cluster configuration of supported cluster stacks, and other
#convenient actions.


_deobfuscate_email = (lambda what: what.replace(' @at@ ', '@')
                                       .replace(' .dot. ', '.')
                                       .replace('@Red Hat.', '@redhat.'))


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


version_parts = (' '.join((package_name(), version)), copyright, '',
                 lambda: author_text().join(("Written by ", ".")))

def version_text(*args, **kwargs):
    args, sep = args + tuple(version_parts[len(args):]), kwargs.get('sep', '\n')
    return sep.join(a() if hasattr(a, '__call__') else a for a in args)
