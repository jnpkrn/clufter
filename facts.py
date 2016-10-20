# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Utility functions wrt. cluster systems in general"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from logging import getLogger

from .utils import args2sgpl
from .utils_func import apply_intercalate

log = getLogger(__name__)


#
# EXECUTABLE KNOWLEDGE ABOUT THE CLUSTER PACKAGES PER SYSTEM/DISTROS
#
# or a bit of a logic programming paradigm with Python...
#
# ... first, define some facts (in suitable data structures):
#

# core hierarchical (sparse!) map:
# system -> distro -> release -> package -> version
#
# The notation should be self-explanatory, perhaps except 'component[extra]'
# (borrowed from the very similar construct of setuptools, there can be more
# "extra traits" delimited with comma) ... simply 'pacemaker[cman]' means that
# such pacemaker is somehow associated with "cman" (more specificially, it is
# intended [compilation flags, etc.] to be used with cman), which apparently
# doesn't match 'pacemaker[coro]' component specification in the input query.
cluster_map = {
    'linux':
        {
            'debian': (
                ((6, ), {
                    # https://packages.debian.org/squeeze/$PACKAGE
                    'corosync':                      (1, 2),
                    'pacemaker[+coro,+hb]':          (1, 0, 9),
                    #---
                    'sys::init-sys':                'sysvinit',
                }),
                ((7, ), {
                    # https://packages.debian.org/wheezy/$PACKAGE
                    'corosync':                      (1, 4),
                    'pacemaker[+coro,+hb]':          (1, 1, 7),
                }),
                ((8, ), {
                    # https://packages.debian.org/jessie/$PACKAGE
                    'corosync':                      (1, 4, 6),
                    #---
                    'sys::init-sys':                'systemd',
                }),
                ((9, ), {
                    # https://packages.debian.org/stretch/$PACKAGE
                    'corosync':                      (2, 3, 5),
                }),
            ),
            'fedora': (
                # see also
                # https://fedoraproject.org/wiki/Releases/$RELEASE/Schedule
                ((13, ), {
                    'corosync':                      (1, 3),
                    'pacemaker[+cman]':              (1, 1, 4),
                    #---
                    'pkg::mysql':                   'mysql-server',
                    #---
                    'cmd::pkg-install':             'yum install -y {packages}',
                    #---
                    'sys::init-sys':                'upstart',
                }),
                ((14, ), {
                    'corosync':                      (1, 4),
                    'pacemaker[+cman]':              (1, 1, 6),
                }),
                ((15, ), {
                    'sys::init-sys':                'systemd',
                }),
                ((17, ), {
                    'corosync':                      (2, 3),
                    'pacemaker[+coro]':              (1, 1, 7),
                    'pcs':                           (0, 9, 1),
                    #'pcs':                           (0, 9, 3),  # updates
                }),
                ((18, ), {
                    'pacemaker[+coro]':              (1, 1, 8),
                    'pcs':                           (0, 9, 27),
                }),
                ((19, ), {
                    'pacemaker[+coro]':              (1, 1, 9),
                    'pcs':                           (0, 9, 36),
                    #'pcs':                           (0, 9, 48),  # updates
                    #---
                    # https://fedoraproject.org/wiki/Features/ReplaceMySQLwithMariaDB
                    'pkg::mysql':                   'mariadb-server',
                }),
                ((20, ), {
                    'pcs':                           (0, 9, 44),
                    #'pcs':                           (0, 9, 102),  # updates
                    #'pcs':                           (0, 9, 115),  # updates
                }),
                ((21, ), {
                    'pacemaker[+coro]':              (1, 1, 12),
                    #'pacemaker[+coro]':              (1, 1, 13),  # updates
                    'pcs':                           (0, 9, 115),
                    #'pcs':                           (0, 9, 137),  # updates
                }),
                ((22, ), {
                    #'pacemaker[+coro]':              (1, 1, 13),  # updates
                    'pcs':                           (0, 9, 139),
                    #'pcs':                           (0, 9, 149),  # updates
                    #---
                    # https://fedoraproject.org/wiki/Changes/ReplaceYumWithDNF
                    'cmd::pkg-install':             'dnf install -y {packages}',
                }),
                ((23, ), {
                    'pacemaker[+coro]':              (1, 1, 13),
                    #'pacemaker[+coro]':              (1, 1, 14),  # updates
                    #'pacemaker[+coro]':              (1, 1, 15),  # updates
                    'pcs':                           (0, 9, 144),
                    #'pcs':                           (0, 9, 149),  # updates
                }),
                ((24, ), {
                    'pacemaker[+coro]':              (1, 1, 14),
                    #'pacemaker[+coro]':              (1, 1, 15),  # updates
                    'pcs':                           (0, 9, 150),
                }),
                #((25, ), {
                #    'corosync':                     (2, 4),
                #}),
            ),
            'redhat': (
                ((6, 0), {
                    'corosync':                      (1, 2),
                    #---
                    'pkg::lvm':                     'lvm2',
                    'pkg::mysql':                   'mysql-server',
                    'pkg::postgresql':              'postgresql-server',
                    'pkg::tomcat':                  'tomcat6',
                    'pkg::virsh':                   'libvirt-client',
                    #---
                    'cmd::pkg-install':             'yum install -y {packages}',
                    #---
                    'sys::init-sys':                'upstart',
                }),
                ((6, 2), {
                    'corosync':                      (1, 4),
                }),
                ((6, 4), {
                    'pcs':                           (0, 9, 26),
                }),
                ((6, 5), {
                    'pacemaker[+cman]':              (1, 1, 10),
                    'pcs':                           (0, 9, 90),
                }),
                ((6, 6), {
                    'pacemaker[+cman]':              (1, 1, 12),
                    'pcs':                           (0, 9, 123),
                }),
                ((6, 7), {
                    'pacemaker[+cman]':              (1, 1, 12),
                    'pcs':                           (0, 9, 139),
                }),
                ((6, 8), {
                    'pacemaker[+cman]':              (1, 1, 14),
                    'pcs':                           (0, 9, 148),
                }),
                ((6, 9), {
                    'pacemaker[+cman]':              (1, 1, 15),  # XXX guess
                }),
                ((7, 0), {
                    'corosync':                      (2, 3),
                    'pacemaker[+coro]':              (1, 1, 10),
                    'pcs':                           (0, 9, 115),
                    #---
                    'pkg::mysql':                   'mariadb-server',
                    'pkg::tomcat':                  'tomcat',  # do not inherit
                    #---
                    'sys::init-sys':                'systemd',
                }),
                ((7, 1), {
                    'pacemaker[+coro]':              (1, 1, 12),
                    'pcs':                           (0, 9, 137),
                }),
                ((7, 2), {
                    'pacemaker[+coro]':              (1, 1, 13),
                    'pcs':                           (0, 9, 143),
                }),
                ((7, 3), {
                    'corosync':                      (2, 4),
                    'pacemaker[+coro]':              (1, 1, 15),
                    'pcs':                           (0, 9, 153),  # 152+patches
                }),
            ),
            'ubuntu': (
                ((13, 4), {
                    # https://packages.ubuntu.com/raring/$PACKAGE
                    'corosync':                      (1, 4),
                    'pacemaker[+coro,+hb]':          (1, 1, 7),
                    #---
                    'sys::init-sys':                'upstart',
                }),
                ((13, 10), {
                    # https://packages.ubuntu.com/saucy/$PACKAGE
                    'corosync':                      (2, 3),
                    'pacemaker[+coro,+hb]':          (1, 1, 10),
                }),
                ((15, 4), {
                    # https://packages.ubuntu.com/vivid/$PACKAGE
                    'pacemaker[+coro,+hb]':          (1, 1, 12),
                    #---
                    'sys::init-sys':                'systemd',
                }),
                ((16, 4), {
                    # https://packages.ubuntu.com/xenial/$PACKAGE
                    'pacemaker[+coro]':              (1, 1, 14),
                    'pcs':                           (0, 9, 149),  # universe
                }),
                ((16, 10), {
                    # https://packages.ubuntu.com/yakkety/$PACKAGE
                    'pacemaker[+coro]':              (1, 1, 15),
                    'pcs':                           (0, 9, 153),  # universe
                }),
            ),
        },
}

supported_dists = cluster_map['linux'].keys()

# mere aliases of the distributions (packages remain the same),
# i.e., downstream rebuilders;
# values (and keys when making "alias" association) in this dict should
# correspond to `platform.linux_distribution(full_distribution_name=0)` output
# and the dict can contain also associated keys obtained as
# `platform.linux_distribution(full_distribution_name=1).lower()`
# or, on top of previous, what's expected to be entered by the user
aliases_dist = {
    # aliases
    # XXX platform.linux_distribution(full_distribution_name=0), i.e.,
    #     short distro names of Scientific Linux et al. needed
    'centos': 'redhat',
    # full_distribution_name=1 (lower-cased) -> full_distribution_name=0
    'red hat enterprise linux server': 'redhat',
    # convenience/choice of common sense or intuition
    'rhel': 'redhat',
}

# in the queries, one can use following aliases to wildcard versions
# of particular packages
aliases_rel = {
    'corosync': {
        'flatiron':   '1',
        'needle':     '2',
    },
    'debian': {  # because of http://bugs.python.org/issue9514 @ 2.6 ?
        'squeeze':    '6',
        'wheezy':     '7',
        'wheezy/sid': '7.999',  # XXX ?
        'jessie':     '8',
    },
    'ubuntu': {
        '13.04':      '13.4',
        'raring':     '13.4',   # Raring Ringtail
        'saucy':      '13.10',  # Saucy Salamander
        '14.04':      '14.4',
        'trusty':     '14.4',   # Trusty Tahr
        'utopic':     '14.10',  # Utopic Unicorn
        '15.04':      '15.4',
        'vivid':      '15.4',   # Vivid Vervet
        'wily':       '15.10',  # Wily Werewolf
        '16.04':      '16.4',
        'xenial':     '16.4',   # Xenial Xerus
        'yakkety':    '16.10',  # Yakkety Yak
    }
}

versions_extra = {
    '__cache__': {},
    'corosync': (
        ((2, 4),
            '+qdevice,+qnet'),
    ),
    'pacemaker': (
        ((1, 1, 8),
            '+schema-1.2'),
        ((1, 1, 12),
            '+acls,+schema-2.0'),
        ((1, 1, 13),
            '+schema-2.3'),
        ((1, 1, 14),
            '+schema-2.4'),
        ((1, 1, 15),
            '+alerts,+schema-2.5'),
    ),
    'pcs': (
        ((0, 9, 145),
            '+node-maintenance'),
        ((0, 9, 148),
            '+utilization'),
        ((0, 9, 150),
            '+wait-cluster-start'),
        ((0, 9, 153),
            # qdevice+qnet preliminary support since 0.9.151, but...
            '+alerts,+qdevice,+qnet'),
    ),
}

#
# ...then, define some executable inference rules, starting with their helpers:
#

def _parse_ver(s):
    name, ver = (lambda a, b=None: (a, b))(*s.split('=', 1))
    if ver:
        try:
            ver = aliases_rel[name][ver]
        except KeyError:
            pass
        ver = tuple(map(int, ver.split('.')))
    return name, ver


def _cmp_ver(v1, v2):
    if v1 and v2:
        v1, v2 = list(reversed(v1)), list(reversed(v2))
        while v1 and v2:
            ret = cmp(v1.pop(), v2.pop())
            if ret:
                return ret
    return 0


def _parse_extra(s, version=None, version_map=versions_extra):
    # Formalized "extra" specification:
    # EXTRA_SPEC(MODS) ::= [ EXTRAS(MODS) ]
    # EXTRAS(MODS)     ::= EXTRA(MODS) | EXTRA(MODS), EXTRAS(MODS)
    # EXTRA(MODS)      ::=(for some modifier in MODS) modifier word
    #
    # depending on the context of use, MODS can be:
    # - '' (empty string): parsing "extra" for public use, i.e.,
    #   when `version` and `version_map` not provided
    # - ''/'+'/'-': parsing "extra" for private use, i.e., when those
    #   parameters are provided
    #
    # `version_map` is a mapping from component to an ordered pairs
    # (VERSION, EXTRA_SPECS(('+', '-'))), where VERSION is encoded as
    # a tuple of numerical components of the version (i.e., result of
    # `_parse_ver`) and '+'/'-' modifier denotes the extras/features
    # being introduced/removed as of a respective version of the
    # component; `version` is a search entry between respective
    # versions here and the intermediate result of this search
    # is an extras snapshot (subsuming all the +/- changes till
    # that moment) as of the closest lower version than `version`.
    #
    # Virtually, the parsed extras are, as a sequence, appended after
    # the snapshot obtained per previous paragraph, and following rules
    # are applied on the resulting ordered sequence:
    #
    #     |- +foo [,...]  ->  foo |- [,...]
    #     |- -foo [,...]  ->      |- [,...]  # warning emitted
    #
    # foo |- +foo [,...]  ->  foo |- [,...]  # idempotency
    # foo |- -foo [,...]  ->      |- [,...]  # elimination
    name, extra = (lambda a, b='': (a, b.rstrip(']')))(*s.split('[', 1))
    allowed_mods, ret, worklist = ' ', set(), []
    if version and version_map:
        allowed_mods = '+-'
        try:
            ret = version_map['__cache__'][name][version]
        except KeyError:
            worklist = list(version_map.get(name, ()))
    else:
        version, version_map = (), {}
    worklist.append((version, extra))
    worklist.reverse()

    while worklist:
        v, es = worklist.pop()
        c = 0
        if worklist:
            c = _cmp_ver(version, v)
        elif version_map:
            # cache the resolved "snapshot" for name and version
            per_comp = version_map['__cache__'].setdefault(name, {})
            per_comp[version] = ret.copy()
        if c >= 0:
            for e in filter(len, (e.strip() for e in es.split(','))):
                if not version:
                    mod = allowed_mods
                else:
                    mod, e = (lambda a, *b: (a, ''.join(b)))(*e)
                if e and mod in allowed_mods:
                    try:
                        (set.remove if mod == '-' else set.add)(ret, e)
                    except KeyError:
                        log.warn("unexpected use of `{0}{1}'".format(mod, e))
                else:
                    log.warn("unexpected use of `{0}{1}',"
                             " unexpected/missing modifier".format(mod, e))
        else:
            worklist[:] = worklist[0:1]

    return name, ret


def infer_error(smth, branches):
    raise RuntimeError("This should not be called")


def infer_sys(sys, branches=None):
    log.debug("infer_sys: {0}: {1}".format(sys, branches))
    # lists of system-level dicts
    # -> list of dist-level dicts pertaining the specified system(s)
    if branches is None:
        branches = [cluster_map]
    if sys == "*":
        return apply_intercalate([b.values() for b in branches])
    return [b[sys] for b in branches if sys in b]


def infer_dist(dist, branches=None):
    # list of dist-level dicts
    # -> list of component-level dicts pertaining the specified dist(s)
    # incl. dist alias resolution
    log.debug("infer_dist: {0}: {1}".format(dist, branches))
    if branches is None:
        branches = infer_sys('*')  # alt.: branches = [cluster_map.values()]
    if dist == '*':
        return apply_intercalate([per_distver[1] for b in branches
                                  for per_dist in b.itervalues()
                                  for per_distver in per_dist])
    ret = []
    dist, dist_ver = _parse_ver(dist)
    try:
        dist = aliases_dist[dist]
    except KeyError:
        pass
    for b in branches:
        for d, d_branches in b.iteritems():
            if d == dist:
                # first time, we (also) traverse whole sequence of per-distro
                # releases, in-situ de-sparsifying particular packages releases;
                # to avoid needlessly repeated de-sparsifying, we are using
                # '__proceeded__' mark to denote already proceeded dicts
                cur_acc = {}
                if '__proceeded__' not in d_branches or dist_ver:
                    for i, (dver, dver_branches) in enumerate(d_branches):
                        if dist_ver:
                            if (_cmp_ver(dist_ver, dver) >= 0 and
                                (i == len(d_branches) - 1
                                or _cmp_ver(dist_ver, d_branches[i+1][0]) < 0)):
                                ret.append(dver_branches)
                                if '__proceeded__' in dver_branches:
                                    break
                                else:
                                    dist_ver = None  # only desparsify since now
                            if '__proceeded__' in dver_branches:
                                continue  # only searching, no hit yet

                        for k, v in dver_branches.iteritems():
                            kk, k_extra = _parse_extra(k, version=v,
                                                       version_map=versions_extra)

                            # prevent leaking of extra from previous cycles
                            prev_extra = cur_acc.get(kk, '')
                            cur_acc.pop("{0}{1}".format(kk, prev_extra), None)

                            k_extra = ','.join(sorted(k_extra)).join("[]" if
                                                                     k_extra
                                                                     else '')
                            cur_acc[kk] = k_extra
                            cur_acc["{0}{1}".format(kk, k_extra)] = v
                        dver_branches.clear()
                        dver_branches.update(cur_acc)
                        dver_branches['__proceeded__'] = '[true]'

                if dist_ver is None and not ret:  # alt. above: dist_ver = ''
                    ret.extend(dver_branches for _, dver_branches in d_branches)
    return ret


def infer_comp(comp, branches=None):
    log.debug("infer_comp: {0}: {1}".format(comp, branches))
    # list of component-level dicts
    # -> list of component-level dicts pertaining the specified comp(s)
    # incl. component version alias resolution
    if branches is None:
        branches = infer_dist('*')  # alt.: branches = [cluster_map.values()]
    if comp == '*':
        return branches
    ret = []
    comp, comp_ver = _parse_ver(comp)
    comp, comp_extra = _parse_extra(comp)
    for b in branches:
        for c, c_ver in b.iteritems():
            c, c_extra = _parse_extra(c)
            if (c == comp
                and (not comp_extra or not comp_extra.difference(c_extra))
                and _cmp_ver(comp_ver, c_ver) == 0):
                    ret.append(b)
                    break

    return ret

rule_error = (0, infer_error)
inference_rules = {
    # type (of clause): (handling priority, handler)
    'error': rule_error,
    'sys':   (1, infer_sys),
    'dist':  (2, infer_dist),
    'comp':  (3, infer_comp),
}


#
# ...and application-specific inference engine:
#

def infer(query, system=None, system_extra=None):
    """Get/infer answers for system-distro-release-package-version queries

    Query grammar is (currently = least resistance, generalization needed):

    QUERY      ::= TERM | TERM WS* '+' WS* QUERY
    TERM       ::= TYPE:SPEC | comp:COMPSPEC  # comp~component
    WS         ::= [ ]                        # whitespace
    TYPE       ::= sys | dist                 # sys~system, dist~distro
    SPEC       ::= NAME | NAME=SUBSPEC
    COMPSPEC   ::= NAME | NAME-EXTRA | NAME=COMPSUBSPEC | NAME-EXTRA=COMPSUBSPEC
    NAME       ::= [a-zA-Z_-]+                # generally anything reasonable
    SUBSPEC    ::= NUMBER '.' NUMBER | '*'    # arbitrary version as such
    NAME-EXTRA ::= NAME '[' EXTRAS ']'
    EXTRAS     ::= NAME | NAME ',' EXTRAS
    COMPSUBSPEC::= NUMBER '.' NUMBER | NUMBER ',' '*'  # arbitrary minor version
    NUMBER     ::= [0-9]+

    with notes:

    - (COMP)SUBSPEC can be defined as a single number, minor version is assumed
      to be 0 in that case, but it's more like a syntactic sugar thant the
      full-fledged grammar case

    - for simplier expressions, several alias resolutions are in place:
        . distro (almost same set of packages known under different names)
        . component version codename (usually to denote whole major releases)

    - for working examples, see the define predicates below

    """
    # XXX trace_back=comp/dist/sys to anchor the result back in the higher sets
    # XXX only AND is supported via '+', also OR ('/'? even though in some uses
    #     '+' denotes this) together with priority control (parentheses) would
    #     be cool :)
    prev, ret = None, None
    q = [p.strip().split(':', 1) for p in query.split('+')]
    if system:
        q.append(('sys', system.lower()))
    if system_extra:
        q.append(('dist', '='.join(system_extra[:2]).lower()))
    q.sort(key=lambda t: inference_rules.get(t[0], rule_error)[0])
    level = ''
    for q_type, q_content in q:
        inference_rule = inference_rules.get(q_type, rule_error)[1]
        if q_type != level:
            prev = ret
        inferred = inference_rule(q_content, prev)
        log.debug("inferred: {0}".format(inferred))
        ret = [i for i in ret if i in inferred] if q_type == level else inferred
        level = q_type
    return ret


#
# and finally, some wrapping predicates:
#

def cluster_pcs_flatiron(*sys_id):
    """Whether particular `sys_id` corresponds to pcs-flatiron cluster system"""
    return bool(infer("comp:corosync=flatiron + comp:pacemaker[cman]", *sys_id))


def cluster_pcs_needle(*sys_id):
    """Whether particular `sys_id` corresponds to pcs-needle cluster system"""
    return bool(infer("comp:corosync=needle + comp:pacemaker[coro]", *sys_id))


def cluster_pcs_1_2(*sys_id):
    """Whether particular `sys_id` corresponds to pacemaker with 1.2+ schema"""
    return bool(infer("comp:pacemaker[schema-1.2]", *sys_id))


def _find_meta(meta, which, *sys_id, **kwargs):
    meta_comp = '::'.join((meta, which))
    res = infer(':'.join(('comp', meta_comp)), *sys_id)
    for i in res:
        if meta_comp in i:
            return i[meta_comp]
    else:
        return kwargs.get('default')


def package(which, *sys_id):
    default, _ = _parse_extra(which)
    return _find_meta('pkg', which, *sys_id, default=default)


def system(which, *sys_id):
    return _find_meta('sys', which, *sys_id, default=which)


def cmd_pkg_install(pkgs, *sys_id):
    # ready to deal with pkgs being a generator
    cmd = _find_meta('cmd', 'pkg-install', *sys_id)
    packages = ' '.join(pkgs)
    return cmd.format(packages=packages) if cmd and packages else ''


cluster_systems = (cluster_pcs_flatiron, cluster_pcs_needle)


def cluster_unknown(*sys_id):
    return not(any(cluster_sys(*sys_id) for cluster_sys in cluster_systems))


def format_dists(verbosity=0, aliases_dist_inv={}, aliases_rel_inv={}):
    # need to flip the translation tables first (if not already)
    if not aliases_dist_inv:
        aliases_dist_inv.update(reduce(
            lambda acc, (k, v): (acc.setdefault(v, []).append(k), acc)[1],
            aliases_dist.iteritems(), {}
        ))
    if not aliases_rel_inv:
        aliases_rel_inv.update((
            k,
            reduce(
                lambda a, (ik, iv): (a.setdefault(iv, []).append(ik), a)[1],
                v.iteritems(), {}
            )
        ) for k, v in aliases_rel.iteritems() if k in supported_dists)

    return '\n'.join('\n\t'.join(
        args2sgpl(
            '\t# aliases: '.join(
                args2sgpl(k, *filter(
                    len, ('|'.join(sorted(aliases_dist_inv.get(k, ()))), )
                ))
            ),
            *tuple(
                '\t# aliases: '.join(
                    args2sgpl(
                        vvv,
                        *filter(
                            len,
                            ('|'.join(sorted(
                                aliases_rel_inv.get(k, {}) .get(vvv, ())
                            )), )
                        )
                    )
                ) for vv in (v if verbosity else (v[0], ('..', ), v[-1]))
                for vvv in ('.'.join(str(i) for i in vv[0]), )
            )
        )
    ) for k, v in sorted(cluster_map['linux'].iteritems()))
