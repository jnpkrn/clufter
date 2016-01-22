# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....filters.cib2pcscmd import attrset_xsl


cib2pcscmd = (
    attrset_xsl("meta_attributes",
                cmd='$pcscmd_pcs, "resource op defaults"',
                inform='"set operation defaults"')
)
