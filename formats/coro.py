# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Corosync executive configuration"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..format import XML


class coroxml(XML):
    """Corosync executive configuration, XML version (corosync.xml)

    See corosync.xml(5).
    """
    # XMLFormat
    root = 'corosync'
    validator_specs = {
        'etree': ''  # XXX no RNG schema handy yet
    }
