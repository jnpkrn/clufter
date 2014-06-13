# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""XML helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from copy import deepcopy
from lxml import etree

from .error import ClufterPlainError
from .utils import selfaware


NAMESPACES = {
    'clufter': 'http://people.redhat.com/jpokorny/ns/clufter',
    'rng':     'http://relaxng.org/ns/structure/1.0',
    'xsl':     'http://www.w3.org/1999/XSL/Transform',
}

xslt_identity = '''\
    <xsl:template match="{0}@*|{0}node()"
                  xmlns:xsl="''' + NAMESPACES['xsl'] + '''">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
       </xsl:copy>
    </xsl:template>'''


class UtilsXmlError(ClufterPlainError):
    pass


def squote(s):
    """Simple quote"""
    return "'" + s + "'"


def namespaced(ns, ident):
    """Return `ident` in Clark's notation denoting `ns` namespace"""
    ret = "{{{0}}}{1}".format(NAMESPACES.get(ns, ns), ident)
    return ret


def nselem(ns, tag, **kwargs):
    return etree.Element(namespaced(ns, tag), **kwargs)

rng_get_start = etree.ETXPath("/{0}/{1}"
                              .format(namespaced('rng', 'grammar'),
                                      namespaced('rng', 'start')))
xmltag_get_localname = lambda tag: etree.QName(tag).localname
xmltag_get_namespace = lambda tag: etree.QName(tag).namespace

RNG_ELEMENT = ("/{0}//{1}".format(namespaced('rng', 'grammar'),
                                  namespaced('rng', 'element'))
               .replace('{', '{{').replace('}', '}}')
               + "[@name = '{0}']")


@selfaware
def rng_pivot(me, et, tag):
    """Given Relax NG grammar etree as `et`, change start tag (in situ!)"""
    start = rng_get_start(et)
    localname = xmltag_get_localname(tag)
    if len(start) != 1:
        raise UtilsXmlError("Cannot change start if grammar's `start' is"
                            " not contained exactly once ({0} times)"
                            .format(len(start)))
    target = etree.ETXPath(RNG_ELEMENT.format(tag))(et)
    if len(target) != 1:
        raise UtilsXmlError("Cannot change start if the start element `{0}'"
                            " is not contained exactly once ({1} times)"
                            .format(localname, len(target)))
    start, target = start[0], target[0]
    parent_start, parent_target = start.getparent(), target.getparent()
    index_target = parent_target.index(target)
    label = me.__name__ + '_' + localname

    # target's content place directly under /grammar wrapped with new define...
    new_define = nselem('rng', 'define', name=label)
    new_define.append(target)
    parent_start.append(new_define)

    # ... while the original occurrence substituted in-situ with the reference
    new_ref = nselem('rng', 'ref', name=label)
    parent_target.insert(index_target, new_ref)

    # ... and finally /grammar/start pointed anew to refer to the new label
    start_ref = nselem('rng', 'ref', name=label)
    start.clear()
    start.append(start_ref)

    return et
