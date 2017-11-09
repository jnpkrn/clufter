# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Utility functions wrt. cluster systems in general"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

try:
    from itertools import zip_longest
except ImportError:  # PY2 backward compatibility
    from itertools import izip_longest as zip_longest
from logging import getLogger

from .error import ClufterPlainError
from .utils import args2sgpl
from .utils_2to3 import basestring, enumerate_u, iter_items, iter_values, \
                        reduce_u
from .utils_func import apply_intercalate

log = getLogger(__name__)

class FactsError(ClufterPlainError):
    pass

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
                    'resource-agents':               (3, 9, 2),
                }),
                ((8, ), {
                    # https://packages.debian.org/jessie/$PACKAGE
                    'corosync':                      (1, 4, 6),
                    'resource-agents':               (3, 9, 3),
                    #---
                    'sys::init-sys':                'systemd',
                }),
                ((9, ), {
                    # https://packages.debian.org/stretch/$PACKAGE
                    'corosync':                      (2, 4, 2),
                    'pacemaker[+coro]':              (1, 1, 16),
                    'pcs':                           (0, 9, 155),
                    'resource-agents':               (4, 0, 0),  # rc1
                }),
                # currently a moving target
                ((10, ), {
                    # https://packages.debian.org/buster/$PACKAGE
                    'pacemaker[+coro]':              (1, 1, 18),  # rc3
                    'pcs':                           (0, 9, 161),
                    'resource-agents':               (4, 0, 1),
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
                    'resource-agents':               (3, 9, 5),
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
                    'resource-agents':               (3, 9, 6),
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
                    #'corosync':                      (2, 4),  # updates
                    'pacemaker[+coro]':              (1, 1, 14),
                    #'pacemaker[+coro]':              (1, 1, 15),  # updates
                    'pcs':                           (0, 9, 150),
                    'resource-agents':               (3, 9, 7),
                }),
                ((25, ), {
                    'corosync':                      (2, 4, 1),
                    #'pacemaker[+coro]':              (1, 1, 16),  # updates
                    'pcs':                           (0, 9, 154),
                }),
                ((26, ), {
                    'corosync':                      (2, 4, 2),
                    'pacemaker[+coro]':              (1, 1, 17),
                    'pcs':                           (0, 9, 156),
                    'resource-agents':               (4, 0, 1),
                }),
                # coming...
                ((27, ), {
                    #'corosync':                      (2, 4, 3),  # updates
                    'pcs':                           (0, 9, 159),
                }),
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
                    # first time the upstream switch to HB agents happened
                    'resource-agents':               (3, 9, 2),
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
                    'resource-agents':               (3, 9, 5),
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
                    'pacemaker[+cman]':              (1, 1, 15),
                    'pcs[-agents-via-pacemaker]':    (0, 9, 155),
                }),
                ((7, 0), {
                    'corosync':                      (2, 3),
                    'pacemaker[+coro]':              (1, 1, 10),
                    'pcs':                           (0, 9, 115),
                    # may differ from latest 6.x
                    'resource-agents':               (3, 9, 5),
                    #---
                    'pkg::mysql':                   'mariadb-server',
                    'pkg::tomcat':                  'tomcat',  # do not inherit
                    #---
                    'sys::init-sys':                'systemd',
                }),
                ((7, 1), {
                    'pacemaker[+coro]':              (1, 1, 12),
                    'pcs':                           (0, 9, 137),
                     # https://bugzilla.redhat.com/1158500
                    'resource-agents[+docker]':      (3, 9, 5),
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
                ((7, 4), {
                    'pacemaker[+coro,+bundle]':      (1, 1, 16),
                    'pcs':                           (0, 9, 158),
                }),
            ),
            'ubuntu': (
                ((13, 4), {
                    # https://packages.ubuntu.com/raring/$PACKAGE
                    'corosync':                      (1, 4),
                    'pacemaker[+coro,+hb]':          (1, 1, 7),
                    'resource-agents':               (3, 9, 2),
                    #---
                    'sys::init-sys':                'upstart',
                }),
                ((13, 10), {
                    # https://packages.ubuntu.com/saucy/$PACKAGE
                    'corosync':                      (2, 3),
                    'pacemaker[+coro,+hb]':          (1, 1, 10),
                }),
                ((14, 4), {
                    # https://packages.ubuntu.com/trusty/$PACKAGE
                    'resource-agents':               (3, 9, 3),
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
                    'resource-agents':               (3, 9, 7),
                }),
                ((16, 10), {
                    # https://packages.ubuntu.com/yakkety/$PACKAGE
                    'pacemaker[+coro]':              (1, 1, 15),
                    'pcs':                           (0, 9, 153),  # universe
                }),
                ((17, 4), {
                    # https://packages.ubuntu.com/zesty/$PACKAGE
                    'corosync':                      (2, 4),
                    'pacemaker[+coro]':              (1, 1, 16),
                    'pcs':                           (0, 9, 155),  # universe
                    'resource-agents':               (4, 0, 0),
                }),
                ((17, 10), {
                    # https://packages.ubuntu.com/artful/$PACKAGE
                    'pcs':                           (0, 9, 159),  # universe
                    'resource-agents':               (4, 0, 1),
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
        'squeeze':      '6',
        'wheezy':       '7',
        'jessie':       '8',
        'stretch':      '9',
        'buster':      '10',
        #'buster/sid':  '10.999',  # XXX ?
        #'bullseye':    '11',
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
        '17.04':      '17.4',
        'zesty':      '17.4',   # Zesty Zapus
        'artful':     '17.10',  # Artful Aardvark
        # https://wiki.ubuntu.com/BionicBeaver/ReleaseSchedule
        #'bionic':     '18.4',
        #'18.04':      '18.4',   # Bionic Beaver
    }
}

versions_extra = {
    '__cache__': {},
    'corosync': (
        ((2, 4),
            '+qdevice,+qnet'),
    ),
    'pacemaker': (
        # see also http://wiki.clusterlabs.org/wiki/ReleaseCalendar
        ((1, 1, 8),
            '+schema-1.2'),
        ((1, 1, 12),
            '+schema-2.0'),  # implies new style ACLs
        ((1, 1, 13),
            '+schema-2.3'),
        ((1, 1, 14),
            '+schema-2.4'),
        ((1, 1, 15),
            '+alerts,+schema-2.5'),
        ((1, 1, 16),
            '+schema-2.6'),
        # coming...
        ((1, 1, 17),
            '+bundle,+schema-2.9'),
    ),
    'pcs': (
        ((0, 9, 123),
            '+acls'),
        ((0, 9, 145),
            '+node-maintenance'),
        ((0, 9, 148),
            '+utilization'),  # https://bugzilla.redhat.com/1158500
        ((0, 9, 150),
            '+wait-cluster-start'),
        ((0, 9, 153),
            # qdevice+qnet preliminary support since 0.9.151, but...
            '+alerts,+qdevice,+qnet'),
        ((0, 9, 155),
            # this also implies support for external/* stonith agents
            '+agents-via-pacemaker'),  # https://github.com/ClusterLabs/pcs/issues/81
        # http://lists.clusterlabs.org/pipermail/users/2017-February/005103.html
        ((0, 9, 156),
            # this is best accompanied with following Pacemaker/crm_diff bugfix
            # https://github.com/ClusterLabs/pacemaker/commit/20a74b9d37
            '+push-diff'),
        # http://lists.clusterlabs.org/pipermail/users/2017-May/005824.html
        ((0, 9, 158),
            # https://bugzilla.redhat.com/1433016
            # and https://bugzilla.redhat.com/1165821, respectively
            '+bundle,+corosync-encryption-forced'),
        # http://oss.clusterlabs.org/pipermail/users/2017-June/005965.html
        ((0, 9, 159),
            # https://bugzilla.redhat.com/1165821
            '-corosync-encryption-forced,+corosync-encryption'),
    ),
    'resource-agents': (
        # http://lists.linux-ha.org/pipermail/linux-ha/2011-June/043321.html
        #((3, 9, 1),
        #    ),
        # http://lists.linux-ha.org/pipermail/linux-ha/2011-June/043416.html
        #((3, 9, 2),
        #    ),
        # http://lists.linux-ha.org/pipermail/linux-ha/2012-May/045193.html
        ((3, 9, 3),
            '+named'),
        # http://lists.linux-ha.org/pipermail/linux-ha/2012-November/046049.html
        ((3, 9, 4),
            '+IPaddr2~IPv6'),
        # http://lists.linux-ha.org/pipermail/linux-ha/2013-February/046461.html
        #((3, 9, 5),
        #    ),
        # http://lists.linux-ha.org/pipermail/linux-ha/2015-January/048523.html
        # XXX clvm
        ((3, 9, 6),
            '+docker'),
        # http://oss.clusterlabs.org/pipermail/users/2016-February/002216.html
        #((3, 9, 7),
        #    ),
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
            log.debug("resolved: {0}".format(ver))
        except KeyError:
            pass
        ver = tuple(map(int, ver.split('.')))
    return name, ver


def _cmp_ver(v1, v2, asymmetric=False):
    """Compare two given encodings of the version

    Parameters:
        v1            first operand (version tuple if not None)
        v2            second operand (version tuple if not None)
        asymmetric    do not compare absolutely, just the prefix match
    """
    if v1 and v2:
        len_v1, len_v2 = len(v1), len(v2)
        len_shorter = len_v1 if len_v1 <= len_v2 else len_v2
        for i, i1, i2 in enumerate_u(zip_longest(v1, v2, fillvalue=0)):
            if i1 == i2:
                continue
            if asymmetric and i > len_shorter:
                break
            return 1 if i1 > i2 else -1
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
        return apply_intercalate([list(iter_values(b)) for b in branches])
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
                                  for per_dist in iter_values(b)
                                  for per_distver in per_dist])
    ret = []
    dist, dist_ver = _parse_ver(dist)
    try:
        dist = aliases_dist[dist]
    except KeyError:
        pass
    for b in branches:
        for d in b:
            if d == dist:
                # first time, we (also) traverse whole sequence of per-distro
                # releases, in-situ de-sparsifying particular packages releases;
                # to avoid needlessly repeated de-sparsifying, we are using
                # '__proceeded__' mark to denote already proceeded dicts
                d_branches = b[d]
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

                        for k, v in iter_items(dver_branches):
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
        for c, c_ver in iter_items(b):
            c, c_extra = _parse_extra(c)
            if c == comp:
                if (isinstance(c_ver, tuple)
                        and _cmp_ver(comp_ver, c_ver, asymmetric=True) > 0
                        or comp_extra and comp_extra.difference(c_extra)):
                    continue
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
        if not q_content:
            raise FactsError("Cannot resolve `{0}' when empty".format(q_type))
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


def component_or_state(which, *sys_id, **kwargs):
    """Return empty string if satisfying component found, diagnostics if not"""
    ret, found = '', infer(':'.join(('comp', which)), *sys_id)
    if not found:
        pkg, extra = _parse_extra(which)
        system, system_extra = sys_id
        ret_acc, sysextra = [], list(system_extra[:2])
        while sysextra:
            found = infer(':'.join(('comp', pkg)), system, sysextra)
            for i in found:
                for j in i:
                    p, e = _parse_extra(j)
                    if p == pkg:
                        ret_item = ''
                        if len(sysextra) == 2:
                            ret_item = p + '='.join(
                                (', '.join(e).join('[]' if e else ''),
                                 '.'.join(str(x) for x in i[j]) if not
                                 isinstance(i[j], basestring) else i[j])
                            )
                        else:
                            ret_item = kwargs.get(
                                'notyetmsg', '({0} yet untracked)'
                            ).format(p)
                        ret_acc.append(ret_item)
                        if len(sysextra) == 1:
                            break
                else:
                    continue
                break
            if ret_acc:
                break
            sysextra.pop()

        if not ret_acc:
            ret = kwargs.get('nohitmsg', '(no hit for {0})').format(pkg)
        else:
            ret = ' / '.join((', '.join(ret_acc),
                              '-'.join(args2sgpl(system, *system_extra))))

    return ret


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
        aliases_dist_inv.update(reduce_u(
            lambda acc, k, v: (acc.setdefault(v, []).append(k), acc)[1],
            iter_items(aliases_dist), {}
        ))
    if not aliases_rel_inv:
        aliases_rel_inv.update((
            k,
            reduce_u(
                lambda a, ik, iv: (a.setdefault(iv, []).append(ik), a)[1],
                iter_items(v), {}
            )
        ) for k, v in iter_items(aliases_rel) if k in supported_dists)

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
    ) for k, v in sorted(iter_items(cluster_map['linux'])))
