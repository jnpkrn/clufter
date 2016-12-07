# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cib2pcscmd filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..facts import infer
from ..filter import XMLFilter
from ..filters._2pcscmd import verbose_ec_test, verbose_inform
from ..utils_xslt import NL, xslt_params


def attrset_xsl(attrset, cmd=None, inform=None):
    return ('''\
    <xsl:if test="{attrset}/nvpair">
        <xsl:choose>
            <xsl:when test="{attrset}/rule">
                <xsl:message>
                    <!-- TODO:PCS -->
                    <xsl:value-of select="concat('WARNING: has to skip rule-based',
                                                ' {attrset} ', @id,
                                                ' (rhbz#1250744)')"/>
                </xsl:message>
            </xsl:when>
            <xsl:otherwise>
''' + (
                (verbose_inform(inform) + '\n' if inform else '')
                +
                ('''<xsl:value-of select='concat("", {cmd})'/>'''
                 if cmd else '')
) + '''
                <xsl:for-each select="{attrset}">
                    <xsl:for-each select="nvpair">
                        <xsl:value-of select='concat(" &apos;",
                                                    @name, "=", @value,
                                                    "&apos;")'/>
                    </xsl:for-each>
                </xsl:for-each>
''' + (
                ('''<xsl:value-of select="'{NL}'"/>''' + '\n'
                 + verbose_ec_test) if cmd and inform else ''
) + '''
            </xsl:otherwise>
        </xsl:choose>
    </xsl:if>
''').format(NL=NL, attrset=attrset, cmd=cmd)


@XMLFilter.deco('cib', 'string-list', defs=dict(
    pcscmd_force=False,
    pcscmd_verbose=True,
    pcscmd_tmpcib='tmp-cib.xml',
    pcscmd_dryrun=False,
))
def cib2pcscmd(flt_ctxt, in_obj):
    """Outputs set of pcs commands to reinstate the cluster per existing CIB"""
    self = flt_ctxt.ctxt_wrapped
    dry_run, tmp_cib = flt_ctxt['pcscmd_dryrun'], flt_ctxt['pcscmd_tmpcib']
    tmp_cib = (tmp_cib or self.defs['pcscmd_tmpcib']) if dry_run else tmp_cib
    return (
        'bytestring',
        flt_ctxt.ctxt_proceed_xslt(
            in_obj,
            textmode=True,
            def_first=xslt_params(
                pcscmd_force=flt_ctxt['pcscmd_force'],
                pcscmd_verbose=flt_ctxt['pcscmd_verbose'],
                pcscmd_tmpcib=flt_ctxt['pcscmd_tmpcib'],
                pcscmd_dryrun=dry_run,
                pcscmd_pcs="pcs -f {0} ".format(tmp_cib) if tmp_cib else "pcs ",

                pcscmd_extra_utilization = bool(infer(
                    'comp:pcs[utilization]',
                    flt_ctxt['system'],
                    flt_ctxt['system_extra'],
                )),
                pcscmd_extra_alerts = bool(infer(
                    'comp:pacemaker[alerts] + comp:pcs[alerts]',
                    flt_ctxt['system'],
                    flt_ctxt['system_extra'],
                )),
            ),
        ),
    )
