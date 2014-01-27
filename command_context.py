# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Command context, i.e., state distributed along filters chain"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging

from .error import ClufterError

log = logging.getLogger(__name__)


class CommandContextError(ClufterError):
    pass


class CommandContext(dict):
    """Object representing command context (WIP: use dict for now)"""
    pass
