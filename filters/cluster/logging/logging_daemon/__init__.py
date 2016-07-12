# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member, xslt_string_mapping

from logging import getLogger
log = getLogger(__name__)

# XXX a bit dirty DRY approach
from os.path import dirname, join
use = join(reduce(lambda a, b: dirname(a), xrange(2), __file__), '__init__.py')
myglobals = dict(__package__=__package__, __name__=__name__)
try:
    execfile(use, myglobals)
except IOError:
    log.error("Unable to refer to `{0}' file".format(use))
    ccs2needlexml_attrs = None  # make it fail later on if ccs2needlexml used
else:
    ccs2needlexml_attrs = myglobals['ccs2needlexml_attrs'] + ('subsys', )

# flatiron -> needle logging subsys mapping
# domain: True (stay as is), False (ditto + warning), string (rename to this)
ccs2needlexml_subsys = {
    'APIDEF': True,
    'CFG':    True,
    'CONFDB': 'CMAP',
    'CPG':    True,
    'PLOAD':  True,
    'SERV':   True,
    'SYNC':   False,
    'SYNCV2': 'SYNC',
    'VOTEQ':  True,
    'YKD':    True,
}

ccs2needlexml = '''\
    <xsl:if test="@name='corosync'
                  and
                  @subsys[
 ''' + (
                  xslt_is_member('.', ccs2needlexml_subsys)
) + '''
                  ]">
        <logger_subsys>
            <xsl:for-each select="@*[
''' + (
                xslt_is_member('name()', ccs2needlexml_attrs)
) + '''
                                 ]">
                <xsl:choose>
                    <xsl:when test="name() != 'subsys'
                                    or
''' + (
                    xslt_is_member('.', (k for k in ccs2needlexml_subsys
                                         if ccs2needlexml_subsys[k] is True))
) + '''                             ">
                        <xsl:copy/>
                    </xsl:when>
                    <xsl:when test="
''' + (
                    xslt_is_member('.', (k for k in ccs2needlexml_subsys
                                         if ccs2needlexml_subsys[k] is False))
) + '''">
                        <xsl:attribute name="{name()}">
                        <xsl:message>
                            <xsl:value-of select="concat('NOTE: Logging subsystem `',
                                                         ., '` originally had',
                                                         ' a different meaning',
                                                         ' but kept as is')"/>
                        </xsl:message>
                        </xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:attribute name="{name()}">
                            <xsl:choose>
''' + (
                            xslt_string_mapping(ccs2needlexml_subsys)
) + '''
                            </xsl:choose>
                        </xsl:attribute>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
        </logger_subsys>
    </xsl:if>
'''

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@logfile', kind='F',
                              desc="log file for ', normalize-space(@name), '")
