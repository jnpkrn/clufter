# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Pacemaker configuration system (pcs) format"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import XML


class pcs(XML):
    """Pacemaker-based cluster stack configuration (as XML/CIB)

    Also known as Pacemaker Configuration System (pcs).
    """
    # XML
    root = 'cib'
    validator_specs = {
        XML.ETREE: 'pacemaker-1.2.rng'
    }


class pcs_prelude(pcs):
    """Private, "unfinished" pacemaker-based cluster stack configuration

    This is a result of ccsflat2pcsprelude filter.
    """


class pcs_compact(pcs):
    """Private, "unfinished" pacemaker-based cluster stack configuration

    This is a result of pcsprelude2pcscompact filter.
    """
