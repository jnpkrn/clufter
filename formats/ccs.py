# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Cluster configuration system (ccs) format"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import XML


class ccs(XML):
    """CMAN-based cluster stack configuration (cluster.conf)

    Sometimes called Cluster Configuration System (ccs).
    """
    # XML
    root = 'cluster'
    validator_specs = {
        XML.ETREE: ''  # XXX no RNG schema handy yet
    }


class ccs_flat(ccs):
    """Private, artificially flattened CMAN-based cluster stack configuration

    Sometimes (ehm, exclusively by me) called Cluster Configuration System Flat.
    This is a result of (one-off!) linearization of nested explicit ordering
    of resources as performed internally by RGManager, and in turn, also
    by the derived helper ccs_flatten (bundled).
    """
    pass
