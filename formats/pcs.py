# -*- coding: UTF-8 -*-
# Copyright 2012 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Pacemaker configuration system (pcs) format"""
__author__ = "Jan Pokorný <jpokorny at redhat dot com>"

from ..format import XML


class pcs(XML):
    """Cman-based cluster stack configuration (cluster.conf)

    Also known as Pacemaker Configuration System (pcs).
    """
    # XML
    root = 'cluster'
