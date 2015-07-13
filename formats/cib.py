# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Pacemaker configuration system/Cluster Information Base (CIB) format"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import dirname, isabs, join
from sys import modules

from ..format import XML
from ..utils import classproperty


class cib(XML):
    """Pacemaker-based cluster stack configuration (as XML/CIB)

    Also known as Pacemaker Configuration System (cib).
    """
    # XML
    root = 'cib'
    validator_specs = {
        XML.ETREE: 'pacemaker-1.2.rng'
    }

    _void_file = 'pacemaker-1.2.minimal'

    @classproperty
    def void_file(cls):
        if not isabs(cls._void_file):
            cls._void_file = join(dirname(modules[cls.__module__].__file__),
                                  cls.root, cls._void_file)
        return cls._void_file


class cib_prelude(cib):
    """Private, "unfinished" pacemaker-based cluster stack configuration

    This is a result of ccsflat2cibprelude filter.
    """


class cib_compact(cib):
    """Private, "unfinished" pacemaker-based cluster stack configuration

    This is a result of cibprelude2cibcompact filter.
    """


class cib_final(cib):
    """Public, "finished" pacemaker-based cluster stack configuration

    This is a result of cib2cibfinal filter.
    """
