# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_xslt import NL, xslt_is_member

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
    <!--
        LOCATION
     -->

    <!-- plain prefers/avoids (XXX could be ordered for prettiness) -->
    <xsl:for-each select="rsc_location[@score]">
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
        <xsl:value-of select="concat('pcs constraint location',
                                     ' ', @rsc,
                                     ' ', $Relationship, ' ', @node)"/>
        <xsl:if test="@score != 'INFINITY'">
            <xsl:value-of select="concat('=', @score)"/>
        </xsl:if>
        <xsl:value-of select="'%(NL)s'"/>
    </xsl:for-each>

    <!-- rule-based location constraint -->
    <xsl:for-each select="rsc_location[rule]">
        <xsl:variable name="Resource" select="@rsc"/>
        <xsl:variable name="ConstraintId" select="@id"/>
        <xsl:variable name="BooleanOp" select="@boolean-op"/>
        <xsl:for-each select="rule">
            <xsl:choose>
                <xsl:when test="@id-ref">
                    <!-- XXX: could eventually be unfolded in-place if found -->
                    <xsl:message
                    >WARNING: skipping location rule provided via reference</xsl:message>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat('pcs constraint location',
                                                 ' ', $Resource,
                                                 ' ', 'rule',
                                                 ' ', 'id=', @id)"/>
                    <xsl:if test="
''' + (
                    xslt_is_member('@role', ('master', 'slave'))
) + '''">
                        <xsl:value-of select="concat(' ', 'role=', @role)"/>
                    </xsl:if>
                    <xsl:value-of select="concat(' constraint-id=',
                                                 $ConstraintId)"/>
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
                                        <xsl:value-of select="concat(' ', @operation, ' ', @attribute)"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="concat(' ', @attribute, ' ', @operation, ' ', @value)"/>
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
                </xsl:otherwise>
            </xsl:choose>
            <xsl:value-of select="'%(NL)s'"/>
        </xsl:for-each>
    </xsl:for-each>


    <!--
        ORDER
     -->

    <!-- plain first-then -->
    <xsl:for-each select="rsc_order[@first and @then]">
        <xsl:value-of select="'pcs constraint order'"/>
        <xsl:if test="@first-action and @first-action != 'start'">
            <xsl:value-of select="concat(' ', @first-action)"/>
        </xsl:if>
        <xsl:value-of select="concat(' ', @first, ' then')"/>
        <xsl:if test="@then-action and @then-action != 'start'">
            <xsl:value-of select="concat(' ', @then-action)"/>
        </xsl:if>
        <xsl:value-of select="concat(' ', @then)"/>
        <xsl:value-of select="concat(' ', 'id=', @id)"/>
        <xsl:if test="@kind">
            <xsl:value-of select="concat(' ', 'kind=', @kind)"/>
        </xsl:if>
        <xsl:if test="@symmetrical">
            <xsl:value-of select="concat(' ', 'symmetrical=', @symmetrical)"/>
        </xsl:if>
        <xsl:value-of select="'%(NL)s'"/>
    </xsl:for-each>

    <!-- resource sets -->
    <xsl:if test="rsc_order[resource_set]">
        <xsl:message
        >WARNING: order constraint with resource sets not supported (yet)</xsl:message>
    </xsl:if>

    <!--
        COLOCATION
     -->
    <!-- plain "with" -->
    <xsl:for-each select="rsc_colocation[@rsc and @with-rsc]">
        <xsl:value-of select="'pcs constraint colocation add'"/>
        <xsl:if test="
''' + (
        xslt_is_member('@rsc-role', ('master', 'slave'))
) + '''">
            <xsl:value-of select="concat(' ', @rsc-role)"/>
        </xsl:if>
        <xsl:value-of select="concat(' ', @rsc, ' with')"/>
        <xsl:if test="
''' + (
        xslt_is_member('@with-rsc-role', ('master', 'slave'))
) + '''">
            <xsl:value-of select="concat(' ', @with-rsc-role)"/>
        </xsl:if>
        <xsl:value-of select="concat(' ', @with-rsc)"/>
        <xsl:if test="@score and not(
''' + (
        xslt_is_member('@score', ('INFINITY', '+INFINITY'))
) + ''')">
            <xsl:value-of select="concat(' ', @score)"/>
        </xsl:if>
        <xsl:value-of select="concat(' ', 'id=', @id)"/>
        <xsl:choose>
            <xsl:when test="@score"/>
            <xsl:when test="@score-attribute">
                <xsl:value-of select="concat(' ', 'score-attribute=',
                                             @score-attribute)"/>
            </xsl:when>
            <xsl:when test="@score-attribute-mangle">
                <xsl:value-of select="concat(' ', 'score-attribute-mangle=',
                                             @score-attribute-mangle)"/>
            </xsl:when>
        </xsl:choose>
        <xsl:value-of select="'%(NL)s'"/>
    </xsl:for-each>

    <!-- resource sets -->
    <xsl:if test="rsc_colocation[resource_set]">
        <xsl:message
        >WARNING: colocation constraint with resource sets not supported (yet)</xsl:message>
    </xsl:if>

''') % dict(
    NL=NL
)
