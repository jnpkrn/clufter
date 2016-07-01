# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, translate_lower, xslt_is_member

cib2pcscmd_datespec = (
    'hours',
    'monthdays',
    'weekdays',
    'yearsdays',
    'months',
    'weeks',
    'years',
    'weekyears',
    'moon',
)

cib2pcscmd = ('''\
    <xsl:choose>
        <!-- plain prefers/avoids (XXX could be ordered for prettiness) -->
        <xsl:when test="@score">
            <xsl:variable name="Relationship">
                <xsl:choose>
                    <xsl:when test="@score = 'INFINITY'
                                    or
                                    @score &gt;= 0">
                        <xsl:value-of select="'prefers'"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="'avoids'"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            <xsl:value-of select="concat($pcscmd_pcs, 'constraint location',
                                        ' ', @rsc,
                                        ' ', $Relationship, ' ', @node)"/>
            <xsl:if test="@score != 'INFINITY'">
                <xsl:value-of select="concat('=', @score)"/>
            </xsl:if>
            <xsl:value-of select="'%(NL)s'"/>
        </xsl:when>

        <!-- rule-based location constraint -->
        <xsl:when test="rule">
            <xsl:variable name="Resource" select="@rsc"/>
            <xsl:variable name="ConstraintId" select="@id"/>
            <xsl:variable name="BooleanOp" select="@boolean-op"/>
            <xsl:for-each select="rule[@id-ref]">
                <!-- XXX: could eventually be unfolded in-place if found -->
                <xsl:message
                >WARNING: skipping location rule provided via reference</xsl:message>
            </xsl:for-each>
            <xsl:for-each select="rule[not(@id-ref)]">
''' + (
                verbose_inform('"new rule/location constraint: ", @id, "/", $ConstraintId')
) + '''
                <xsl:choose>
                    <xsl:when test="position() = 1">
                        <xsl:value-of select="concat(
                                                $pcscmd_pcs, 'constraint location',
                                                ' ', $Resource,
                                                ' ', 'rule',
                                                ' ', 'id=', @id,
                                                ' ', 'constraint-id=', $ConstraintId
                                            )"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <!-- subsequent per-constraint rules;
                            see https://bugzilla.redhat.com/1223404 -->
                        <xsl:value-of select="concat(
                                                $pcscmd_pcs, 'constraint rule add',
                                                ' ', $ConstraintId,
                                                ' ', 'id=', @id
                                            )"/>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:if test="
''' + (
                xslt_is_member(translate_lower('@role'),
                               ('master', 'slave'))
) + '''">
                    <xsl:value-of select="concat(' ',
''' + (
                        translate_lower('@role')
) + ''')"/>
                </xsl:if>
                <xsl:choose>
                    <xsl:when test="@score">
                        <xsl:value-of select="concat(' score=', @score)"/>
                    </xsl:when>
                    <xsl:when test="@score-attribute">
                        <xsl:value-of select="concat(' score-attribute=',
                                                    @score-attribute)"/>
                    </xsl:when>
                </xsl:choose>

                <xsl:if test="rule">
                    <xsl:message
                    >WARNING: cannot handle nested rules (yet)</xsl:message>
                </xsl:if>

                <xsl:for-each select="descendant::expression|descendant::date_expression">
                    <xsl:if test="count(preceding-sibling::expression|preceding-sibling::date_expression) &gt; 0">
                        <xsl:value-of select="concat(' ', $BooleanOp, ' ')"/>
                    </xsl:if>
                    <xsl:choose>
                        <xsl:when test="name() = 'expression'">
                            <xsl:choose>
                                <xsl:when test="
''' + (
                                xslt_is_member('@operation', ('defined', 'not_defined'))
) + '''">
                                    <xsl:value-of select='concat(" ", @operation,
                                                                " &apos;", @attribute, "&apos;")'/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select='concat(" &apos;", @attribute, "&apos;",
                                                                " ", @operation)'/>
                                    <xsl:if test="
''' + (
                                    xslt_is_member('@type', ('string', 'number', 'version'))
) + '''">
                                        <xsl:value-of select="concat(' ', @type)"/>
                                    </xsl:if>
                                    <xsl:value-of select='concat(" &apos;", @value, "&apos;")'/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:when>
                        <xsl:when test="name() = 'date_expression'">
                            <xsl:choose>
                                <xsl:when test="@operation = 'in_range'">
                                    <xsl:value-of select="' date in_range '"/>
                                    <xsl:choose>
                                        <xsl:when test="@end">
                                            <!-- see https://bugzilla.redhat.com/1182358 -->
                                            <xsl:if test="@start">
                                                <xsl:value-of select="@start"/>
                                            </xsl:if>
                                            <xsl:value-of select="concat(' to ', @end)"/>
                                        </xsl:when>
                                        <xsl:when test="duration">
                                            <xsl:value-of select="concat(@start, ' to ')"/>
                                            <xsl:for-each select="duration/@*[
''' + (
                                            xslt_is_member('name()', cib2pcscmd_datespec)
) + ''']">
                                                <xsl:value-of select="concat(' ', name(), '=', .)"/>
                                            </xsl:for-each>
                                        </xsl:when>
                                    </xsl:choose>
                                </xsl:when>
                                <xsl:when test="@operation = 'gt'">
                                    <xsl:value-of select="concat(' date gt ', @start)"/>
                                </xsl:when>
                                <xsl:when test="@operation = 'lt'">
                                    <xsl:value-of select="concat(' date lt ', @end)"/>
                                </xsl:when>
                                <xsl:when test="@operation = 'date_spec'">
                                    <xsl:value-of select="' date-spec '"/>
                                        <xsl:for-each select="date_spec/@*[
''' + (
                                        xslt_is_member('name()', cib2pcscmd_datespec)
) + ''']">
                                            <xsl:value-of select="concat(' ', name(), '=', .)"/>
                                        </xsl:for-each>
                                </xsl:when>
                            </xsl:choose>
                        </xsl:when>
                    </xsl:choose>
                </xsl:for-each>
                <xsl:value-of select="'%(NL)s'"/>
''' + (
                verbose_ec_test
) + '''
            </xsl:for-each>
        </xsl:when>
    </xsl:choose>

''') % dict(
    NL=NL,
)
