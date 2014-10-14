# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


pcsprelude2pcs = '''\
    <clufter:descent-mix preserve-rest="true"/>
    <!-- strip empty optional elements -->
    <xsl:template match="fencing-topology[count(*) = 0]"/>
'''
