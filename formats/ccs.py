# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Cluster configuration system (ccs) format"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import XML


class ccs(XML):
    """Cman-based cluster stack configuration (cluster.conf)

    Sometimes called Cluster Configuration System (ccs).
    """
    # XML
    root = 'cluster'
    validator_specs = {
        'etree': ''  # XXX no RNG schema handy yet
    }


class flatccs(ccs):
    """Cman-based cluster stack configuration (cluster.conf)

    Sometimes (ehm, exclusively by me) called Cluster Configuration System Flat.
    """
    pass
