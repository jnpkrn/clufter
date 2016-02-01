# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Wrapper around standard lxml.etree static methods"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from lxml import etree

etree_XSLT_safe = lambda _input, **kwargs: \
    etree.XSLT(_input,
               **dict(access_control=etree.XSLTAccessControl.DENY_ALL,
                      **kwargs))

etree_parser_safe_kwargs = dict(
    no_network=True,
    #resolve_entities=False,
)

etree_parser_safe = etree.XMLParser(**etree_parser_safe_kwargs)

etree_parser_safe_unblanking = etree.XMLParser(**dict(
    remove_blank_text=True,
    **etree_parser_safe_kwargs
))
