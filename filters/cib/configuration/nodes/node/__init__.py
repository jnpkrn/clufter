# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....filters.cib2pcscmd import attrset_xsl

cib2pcscmd = ((
    attrset_xsl("instance_attributes",
                cmd='$pcscmd_pcs, "property set"',
                inform='"set properties for ", @uname, " node"')

) + '''
    <!-- XXX "pcs resource utilization" not supported with majority
             of pcs versions -->
''' + (
    attrset_xsl("utilization",
                cmd='$pcscmd_pcs, "node utilization -h",'
                    ' " &gt;/dev/null &amp;&amp; ",'
                    ' $pcscmd_pcs, "node utilization ",'
                    ' @uname',
                inform='"set utilization for resource: ", @uname, " node"')
))
