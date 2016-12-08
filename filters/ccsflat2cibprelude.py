# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccsflat2cibprelude filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..facts import cluster_pcs_flatiron, component_or_state, package, system
from ..filter import XMLFilter
from ..utils_xslt import xslt_params

from os.path import join


# XXX temporary hack with plain ccs;
# check that it is indeed ccs-flat, by exploring flt_ctxt?
@XMLFilter.deco('ccs-flat', 'cib-prelude')
def ccsflat2cibprelude(flt_ctxt, in_obj):
    sys_pair = flt_ctxt['system'], flt_ctxt['system_extra']
    return (
        'etree',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            def_first=xslt_params(
                pcscmd_cman=cluster_pcs_flatiron(*sys_pair),
                pcscmd_init_sys=system('init-sys', *sys_pair),
                pcscmd_tomcat_catalina_home=join(
                    '/usr/share',
                    package('tomcat', *sys_pair)
                ),
                pcscmd_named_qual=component_or_state('resource-agents[named]',
                                                     nohitmsg='', *sys_pair),
            )
        )
    )
