# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""*2pcscmd filters helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from xml.sax.saxutils import escape

from ..utils_xslt import NL

verbose_prefix = ':: '
verbose_OK = verbose_prefix + 'OK'
verbose_FAILURE = verbose_prefix + 'FAILURE'

ec_test = "{0}{1}:{1}".format(
    escape("test $? -eq 0 && echo '{verbose_OK}' || echo '{verbose_FAILURE}'"
           .format(verbose_OK=verbose_OK, verbose_FAILURE=verbose_FAILURE),
           {"'": "&apos;", '"': "&quot;"}),
    NL
)

verbose_ec_test = '''\
    <xsl:if test="$pcscmd_verbose">
        <xsl:value-of select='"%(ec_test)s"'/>
    </xsl:if>
''' % dict(
    ec_test=ec_test
)

def verbose_inform(what):
    return '''\
    <xsl:if test="$pcscmd_verbose">
        <xsl:value-of select='concat("echo &apos;%(verbose_prefix)s",
                                     %(what)s,
                                     "&apos;%(NL)s")'/>
    </xsl:if>
''' % dict(
    what=what or '""',
    verbose_prefix=verbose_prefix or '""',
    NL=NL,
)


def coro2pcscmd(**kwargs):
    descent = lambda w: \
        '<clufter:descent-mix at="{what}"/>'.format(
            what=kwargs.get(w) or w
        ) if w in kwargs else ''
    return ('''\
    <xsl:variable name="ClusterName" select="string(@name
                                                    |totem/@cluster_name)"/>
    <xsl:if test="not($pcscmd_dryrun)">
        <xsl:if test="not($pcscmd_noauth)">
''' + (
            verbose_inform('"auth cluster: ", $ClusterName')
) + '''
            <xsl:value-of select="'pcs cluster auth'"/>

            %(descent_node)s
            <xsl:if test="$pcscmd_force">
                <xsl:value-of select="' --force'"/>
            </xsl:if>
            <xsl:value-of select="'%(NL)s'"/>
''' + (
            verbose_ec_test
) + '''
        </xsl:if>
        <xsl:if test="not($pcscmd_noguidance)">
            <!-- see rhbz#1210833 -->
''' + (
            verbose_inform('"check cluster includes local machine: ", $ClusterName')
) + r'''
            <xsl:value-of select="concat(
                'for l in $(comm -12',
                    ' &lt;(python -m json.tool /var/lib/pcsd/pcs_users.conf',
                        ' | sed -n &quot;s|^\s*\&quot;[^\&quot;]\+\&quot;:\s*\&quot;\([0-9a-f-]\+\)\&quot;.*|\1|1p&quot;',
                        ' | sort)',
                    ' &lt;(python -m json.tool /var/lib/pcsd/tokens',
                        ' | sed -n &quot;s|^\s*\&quot;[^\&quot;]\+\&quot;:\s*\&quot;\([0-9a-f-]\+\)\&quot;.*|\1|1p&quot;',
                        ' | sort)',
                ') @SENTINEL@; do %(NL)s',
                'grep -Eq &quot;$(python -m json.tool /var/lib/pcsd/tokens',
                    ' | sed -n &quot;s|^\s*\&quot;\([^\&quot;]\+\)\&quot;:\s*\&quot;${l}\&quot;.*|\1|1p&quot;)&quot;',
                    ' - &lt;&lt;&lt;&quot;')"/>
            %(descent_node)s
            <xsl:value-of select="concat(
                '&quot; &amp;&amp; break%(NL)s',
                'false%(NL)s',
                'done || {%(NL)s',
                'echo &quot;WARNING: cluster being created ought to include this very local machine&quot;%(NL)s',
                'read -p &quot;Do you want to continue [yN] (60s timeout): &quot; -t 60 || :%(NL)s',
                'test &quot;${REPLY}&quot; = &quot;y&quot; || kill -INT $$%(NL)s',
                '}%(NL)s:%(NL)s'
            )"/>
        </xsl:if>
''' + (
        verbose_inform('"new cluster: ", $ClusterName')
) + '''
        <xsl:value-of select="'pcs cluster setup'"/>
        <xsl:choose>
            <xsl:when test="$pcscmd_enable">
                <xsl:value-of select="' --enable'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:message>%(msg_enable)s</xsl:message>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="concat(' --name ', $ClusterName)"/>

        %(descent_node)s
        %(descent_cman)s
        %(descent_totem)s
        %(descent_quorum)s
        <xsl:value-of select="'%(NL)s'"/>

        <xsl:choose>
            <xsl:when test="$pcscmd_start_wait &gt; 0">
''' + (
                verbose_inform('"starting cluster and waiting for it to come up: ", $pcscmd_start_wait, " seconds"')
) + '''
            </xsl:when>
            <xsl:otherwise>
''' + (
                verbose_inform('"starting cluster"')
) + '''
            </xsl:otherwise>
        </xsl:choose>

        <xsl:value-of select="'pcs cluster start --all'"/>
        <xsl:if test="$pcscmd_start_wait &gt; 0">
            <xsl:choose>
                <xsl:when test="$pcscmd_extra_wait_cluster_start">
                    <xsl:value-of select="concat(' --wait=',
                                                 $pcscmd_start_wait)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat(' &amp;&amp; sleep ',
                                                  $pcscmd_start_wait)"/>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:value-of select="'%(NL)s'"/>
''' + (
            verbose_ec_test
) + '''
        </xsl:if>
    </xsl:if>
''') % dict(
    NL=NL,
    msg_enable="NOTE: cluster infrastructure services not enabled"
               " at this point, which can be changed any time by issuing"
               " `pcs cluster enable --all`",
    **dict(('descent_' + k, descent(k))
           for k in ('cman', 'node', 'quorum', 'totem'))
)
