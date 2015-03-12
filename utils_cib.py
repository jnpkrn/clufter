# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""CIB helpers, mainly used in the filter definitions"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from .error import ClufterError

class ResourceSpecError(ClufterError):
    pass


class ResourceSpec(object):
    """Representation of simplified resource specification"""
    # see also pcs/resource.py:resource_list_available
    #                          get_full_ra_type
    # note however that Pacemaker internally prefers this notation:
    # class + class == "ocf"?("::" + provider):"" + ":" + type
    # (i.e., double colon), as per
    # pacemaker/lib/pengine/native.c:{native_print_xml,native_print,
    #                                 get_rscs_brief}
    def __init__(self, spec):
        split = spec.replace('::', ':', 1).split(':', 3)
        try:
            self._type = split.pop()
            maybe_class = split.pop()
            self._class = maybe_class if not(split) else split.pop()
            self._provider = maybe_class if self._class == 'ocf' else None
        except IndexError:
            raise ResourceSpecError("Invalid spec: {0}".format(spec))

    @property
    def res_class(self):
        return self._class

    @property
    def res_provider(self):
        if self._class != 'ocf':
            raise ResourceSpecError("No provider for class `ocf'")
        return self._provider

    @property
    def res_type(self):
        return self._type

    @property
    def xsl_attrs(self):
        ret = ('<xsl:attribute name="class">{0}</xsl:attribute>'
               .format(self._class))
        if self._provider is not None:
            ret += ('<xsl:attribute name="provider">{0}</xsl:attribute>'
                    .format(self._provider))
        ret += ('<xsl:attribute name="type">{0}</xsl:attribute>'
                .format(self._type))
        return ret

    @property
    def xsl_attrs_select(self):
        ret = "@class='{0}'".format(self._class)
        if self._provider is not None:
            ret += " and @provider='{0}'".format(self._provider)
        ret += " and @type='{0}'".format(self._type)
        return ret


def rg2hb_xsl(dst, src, req=False, op=False):
    """Emit XSL snippet yielding nvpair-encoded HB RA parameter from RG one

    Parameters:
        req    valid values: False, True, abs (use raw `src` instead)
    """
    assert req in (False, True, abs), "Invalid `req` param"
    return (('''\
            <xsl:if test="@{src}">
''' if not req else '') + (('''\
            <!-- {dst} ~ {src} -->
            <nvpair id="{{concat($Prefix, '-ATTRS-{dst}')}}"
                    name="{dst}"
''' + ('''\
                    value="{{@{src}}}"/>
''' if req is not abs else '''\
                    value="{src}"/>
''')) if not op else ('''\
            <!-- op:{dst} ~ {src} -->
            <op id="{{concat($Prefix, '-OP-{dst}')}}"
                name="{dst}"
                interval="0"
''' + ('''\
                timeout="{{concat(@{src}, 's')}}"/>
''' if req is not abs else '''\
                timeout="{src}"/>
'''))) + ('''\
            </xsl:if>
''' if not req else '')).format(dst=dst, src=src)
