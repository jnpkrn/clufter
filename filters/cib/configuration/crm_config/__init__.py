# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, xslt_is_member

# http://clusterlabs.org/doc/en-US/Pacemaker/1.1-pcs/html-single/Pacemaker_Explained/#_cluster_options
cib2pcscmd_whitelist = (
    'no-quorum-policy',
    'batch-limit',
    'migration-limit',
    'symmetric-cluster',
    'stop-all-resources',
    'stop-orphan-resources',
    'stop-orphan-actions',
    'start-failure-is-fatal',
    'enable-startup-probes',
    'maintenance-mode',
    'stonith-enabled',
    'stonith-action',
    'stonith-timeout',
    'cluster-delay',
    'dc-deadtime',
    'cluster-recheck-interval',
    'pe-error-series-max',
    'pe-warn-series-max',
    'pe-input-series-max',
    'remove-after-stop',
    'startup-fencing',
    #'election-timeout',
    #'shutdown-escalation',
    #'crmd-integration-timeout',
    #'crmd-finalization-timeout',
    'crmd-transition-delay',
    #'default-resource-stickiness',
    #'is-managed-default',
    #'default-action-timeout',
)

cib2pcscmd = ('''\
    <xsl:for-each select="cluster_property_set">
        <xsl:for-each select="nvpair">
            <!-- unfortunately pcs will throw away the rest of name-value
                 pairs when first unknown observed; alternatively a single
                 command with "force" -->
            <xsl:choose>
                <xsl:when test="
''' + (
                    xslt_is_member('@name', cib2pcscmd_whitelist)
) + '''">
''' + (
                    verbose_inform('"set singleton cluster property: ", @name')
) + '''
                    <xsl:value-of select='concat($pcscmd_pcs, "property set")'/>
                    <xsl:if test="$pcscmd_force">
                        <xsl:value-of select="' --force'"/>
                    </xsl:if>
                    <xsl:value-of select='concat(" &apos;", @name, "=", @value, "&apos;")'/>
                    <xsl:value-of select="'%(NL)s'"/>
''' + (
                    verbose_ec_test
) + '''
                </xsl:when>
                <xsl:otherwise>
                    <xsl:message>
                        <xsl:value-of select="concat(
                                                  'WARNING: dropping non-whitelisted cluster property: `',
                                                   @name,
                                                   '`'
                                              )"/>
                    </xsl:message>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:for-each>
''') % dict(
    NL=NL,
)

###

from ....utils_2to3 import execfile
from ....utils_prog import dirname_x
from ....utils_xslt import xslt_is_member

from logging import getLogger
log = getLogger(__name__)

# XXX a bit dirty DRY approach
from os.path import join
use = join(dirname_x(__file__, 2), '__init__.py')
myglobals = dict(__package__=__package__, __name__=__name__)
try:
    execfile(use, myglobals)
except IOError:
    log.error("Unable to refer to `{0}' file".format(use))
    cib_revitalize_deprecated_props_cluster = None  # make it fail later
else:
    cib_revitalize_deprecated_props_cluster = \
        myglobals['cib_revitalize_deprecated_props_cluster']

cib_revitalize = ('''\
    <xsl:copy>
        <xsl:for-each select="cluster_property_set">
            <xsl:if test="not(
                           count(nvpair[
''' + (
                                  xslt_is_member('@name',
                                                 cib_revitalize_deprecated_props_cluster)
) + '''
                              ]) = count(nvpair)
                          ) and not(@id-ref)">
                <xsl:copy>
                    <xsl:copy-of select="@*"/>
                    <xsl:apply-templates select="rule"/>
                    <xsl:apply-templates select="nvpair[not(
''' + (
                                                     xslt_is_member('@name',
                                                                    cib_revitalize_deprecated_props_cluster)
) + ''')]"/>
                    <xsl:apply-templates select="score"/>
                </xsl:copy>
            </xsl:if>
        </xsl:for-each>
    </xsl:copy>
''')
