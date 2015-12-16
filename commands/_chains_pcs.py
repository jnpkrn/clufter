# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Chains of filters used in *2pcs* commands"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..utils import args2sgpl, args2unwrapped, tuplist
from ..utils_func import apply_aggregation_preserving_passing_depth

terminalize = lambda args: \
    apply_aggregation_preserving_passing_depth(
        lambda i, d:
            filter(tuplist, i[:-1])
            + tuple([args.pop() if not tuplist(i[-1]) else i[-1]])
    )


def cast_output(chain):
    def cast_output_inner(*args):
        args = list(args)
        args.reverse()
        ret = terminalize(args)(chain)
        return ret
    return cast_output_inner


ccsflat2cibfinal_chain_exec = lambda cont=(): \
    ('ccs-revitalize',
        ('ccsflat2cibprelude',
            ('cibprelude2cibcompact',
                ('cibcompact2cib',
                    (args2unwrapped('cib2cibfinal', *args2sgpl(cont)))))))
ccsflat2cibfinal_chain = ccsflat2cibfinal_chain_exec()
ccsflat2cibfinal_output = cast_output(ccsflat2cibfinal_chain)

cib2pcscmd_chain_exec = lambda cont=(): \
    ('cib-revitalize',
        ('cib-meld-templates',
            (args2unwrapped('cib2pcscmd', *args2sgpl(cont)))))
cib2pcscmd_chain = cib2pcscmd_chain_exec()
cib2pcscmd_output = cast_output(cib2pcscmd_chain)

ccsflat2pcscmd_chain = (ccsflat2cibfinal_chain_exec(cib2pcscmd_chain))
ccsflat2pcscmd_output = cast_output(ccsflat2pcscmd_chain)
