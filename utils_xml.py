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
    'rng': 'http://relaxng.org/ns/structure/1.0'
}


class UtilsXmlError(ClufterPlainError):
    pass


@selfaware
def rng_pivot(me, et, tag):
    """Given Relax NG grammar etree as `et`, change start tag (in situ!)"""
    start = et.xpath("/rng:grammar/rng:start", namespaces=NAMESPACES)
    if len(start) != 1:
        raise UtilsXmlError("Cannot change start if grammar's `start' is"
                            " not contained exactly once ({0} times)"
                            .format(len(start)))
    target = et.xpath("//rng:element[@name = '{0}']".format(tag),
                      namespaces=NAMESPACES)
    if len(target) != 1:
        raise UtilsXmlError("Cannot change start if the start element `{0}'"
                            " is not contained exactly once ({1} times)"
                            .format(tag, len(target)))
    start, target = start[0], target[0]
    parent_start, parent_target = start.getparent(), target.getparent()
    index_target = parent_target.index(target)
    label = me.__name__ + '_' + tag

    # target's content place directly under /grammar wrapped with new define...
    new_define = etree.Element('define', name=label)
    new_define.append(target)
    parent_start.append(new_define)

    # ... while the original occurrence substituted in-situ with the reference
    new_ref = etree.Element('ref', name=label)
    parent_target.insert(index_target, new_ref)

    # ... and finally /grammar/start pointed anew to refer to the new label
    start_ref = deepcopy(new_ref)
    start.clear()
    start.append(start_ref)

    return et
