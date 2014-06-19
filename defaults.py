# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Some usage-agnostic constants"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os import environ

EDITOR = environ.get('EDITOR', '')
