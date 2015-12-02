# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

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

ccs2needlexml = '''\
    <xsl:if test="@name='corosync' and @subsys">
        <logger_subsys>
            <xsl:copy-of select="@*[
''' + (
                xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']"/>
        </logger_subsys>
    </xsl:if>
'''

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@logfile', kind='F',
                              desc="log file for ', normalize-space(@name), '")
