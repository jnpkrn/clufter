# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base filter stuff (metaclass, decorator, etc.)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from os.path import dirname, join
from copy import deepcopy
from collections import OrderedDict, defaultdict

from lxml import etree

from .plugin_registry import PluginRegistry
from .utils import ClufterError, head_tail, hybridproperty, filtervarspop

log = logging.getLogger(__name__)

DEFAULT_ROOT_DIR = join(dirname(__file__), 'filters')

CLUFTER_NS = 'http://people.redhat.com/jpokorny/ns/clufter'
XSL_NS = 'http://www.w3.org/1999/XSL/Transform'

# XXX: consult standard/books
_TOP_LEVEL_XSL = (
    'import',
    'include',
    'key',
    'namespace-alias',
    'attribute-set',
    'variable',
    'output',
    'template',
    'strip-space'
)
TOP_LEVEL_XSL = ["{{{0}}}{1}".format(XSL_NS, e) for e in _TOP_LEVEL_XSL]


class FilterError(ClufterError):
    pass


class filters(PluginRegistry):
    """Filter registry (to be used as a metaclass for filters)"""
    pass


class Filter(object):
    """Base for filters performing the actual conversion

    Base principles:
        - protocols: string label denoting how to int-/externalize
        - create filter instance = pass particular formats,
          all = start conversion
    """
    __metaclass__ = filters

    def __init__(self, in_format, out_format):
        self._in_format, self._out_format = in_format, out_format

    @hybridproperty
    def in_format(this):
        """Input format identifier/class for the filter"""
        return this._in_format

    @hybridproperty
    def out_format(this):
        """Output format identifier/class for the filter"""
        return this._out_format

    def __call__(self, in_obj, **kwargs):
        """Default is to use a function decorated with `deco`"""
        out_decl = self._fnc(self, in_obj, **kwargs)
        return self.out_format(*out_decl)

    @classmethod
    def deco(cls, in_format, out_format):
        """Decorator as an easy factory of actual filters"""
        def deco_fnc(fnc):
            log.debug("Filter: deco for {0}"
                      .format(fnc))
            attrs = {
                '__module__': fnc.__module__,
                '__doc__': fnc.__doc__,
                '_in_format': in_format,
                '_out_format': out_format,
                '_fnc': staticmethod(fnc),
            }
            # optimization: shorten type() -> new() -> probe
            ret = cls.probe(fnc.__name__, (cls, ), attrs)
            return ret
        return deco_fnc


def tag_log(s, elem):
    """Logging helper"""
    return s.format(elem.tag, ', '.join(':'.join(i) for i in elem.items()))


class XMLFilter(Filter):
    @staticmethod
    def _traverse(in_fmt, walk, walk_default=None, et=None, preprocess=lambda s, n, r: s,
                  proceed=lambda *x: x,
                  postprocess=lambda x: x[0] if len(x) == 1 else x):
        """Generic traverse through XML as per symbols within schema tree"""
        tree_stack = [('', (None, walk), OrderedDict())]
        skip_until = []
        if walk_default is None:
            skip_until = [('start', tag) for tag in walk]
        et = et or in_fmt('etree')

        for context in etree.iterwalk(et, events=('start', 'end')):
            event, elem = context
            log.debug("Got: {0} {1}".format(event, elem.tag))
            if skip_until and (event, elem.tag) not in skip_until:
                continue
            log.debug("Not skipped: {0}".format(elem.tag))
            skip_until = ()  # reset skipping any time we get further
            if event == 'start':
                # going down
                log.debug(tag_log("Moving downwards: {0} ({1})", elem))
                if elem.tag in tree_stack[-1][1][1] or walk_default is not None:
                    if elem.tag not in tree_stack[-1][1][1]:
                        log.debug("Not")
                        walk_new_sym, walk_new_rest = walk_default, tree_stack[-1][1][1].copy()
                    else:
                        walk_new_sym, walk_new_rest = tree_stack[-1][1][1][elem.tag]
                    walk_new_sym = preprocess(walk_new_sym, elem.tag, tree_stack[-1][1][0])
                    tree_stack[-1][1][1][elem.tag] = (walk_new_sym, walk_new_rest)
                    tree_stack.append((elem.tag, (walk_new_sym, walk_new_rest), OrderedDict()))
                    if walk_new_rest is {}:
                        # safe optimization
                        skip_until = [('end', elem.tag)]
                # XXX: optimization prunning, probably no good
                #else:
                #    skip_until = [('end', tag) for tag in tree_stack[-1][1][1]]
                #    skip_until = [('end', elem.tag)]
                #    log.debug("Skipping (A) until: {0}".format(skip_until))

            else:
                # going up
                log.debug(tag_log("Moving upwards: {0} ({1})", elem))
                log.debug("Expecting {0}".format(elem.tag))
                if elem.tag == tree_stack[-1][0]:
                    walk, children = tree_stack.pop()[1:3]
                    tree_stack[-1][2][elem] = proceed(walk[0], elem, children)
                    log.debug("Proceeded {0}".format(
                              etree.tostring(tree_stack[-1][2][elem]).replace('\n', '')))
                # XXX: optimization prunning, probably no good
                #else:
                #    skip_until = [('end', tree_stack[-1][0])]
                #    log.debug("Skipping (C) until: {0}".format(skip_until))

        ret = tree_stack[-1][2].values()
        return postprocess(ret)

    @staticmethod
    def _xslt_preprocess(sym, name, parent_sym=None):
        """Preprocessing of schema tree XSLT snippets to real (sub)templates

        If callable is observed instead of XSLT snippet, keep it untouched.
        Used by `proceed_xslt` and `get_template` methods (hence class-wide).
        """
        if isinstance(sym, tuple):
            return sym  # already proceeded
        if isinstance(sym, basestring):
            log.debug("preprocessing {0}".format(sym))
            # XXX <xsl:output method="xml"
            # XXX memoize as a constant + deepcopy
            sym = ('<clufter:snippet'
                   ' xmlns:xsl="{0}"'
                   ' xmlns:clufter="{1}">'
                   ' {2}'
                   ' </clufter:snippet>'.format(XSL_NS, CLUFTER_NS, sym))
            ret = etree.XML(sym)
            hooks = OrderedDict()
            toplevel = []

            #if len(ret) and parent_sym:
            #    top = filter(lambda x: x.tag in TOP_LEVEL_XSL, ret)
            #    for e in top:
            #        toplevel.append(e)
            #        ret.remove(e)

            if parent_sym and isinstance(parent_sym[0], etree._Element):
                top = filter(lambda x: x.tag in TOP_LEVEL_XSL, parent_sym[0])
                for e in top:
                    print "at", sym, "appending", etree.tostring(e)
                    ret.append(deepcopy(e))
                #for e in toplevel:
                #    parent_sym[0].append(e)

            log.debug("walking {0}".format(etree.tostring(ret)))
            for event, elem in etree.iterwalk(ret, events=('start', )):
                # XXX xpath/specific tag filter
                # register each recurse point at the tag required
                # so it can be utilized in bottom-up pairing (from
                # particular definitions to where it is expected)

                # not needed
                #if elem is ret:
                #    continue
                log.debug("Got {0}".format(elem.tag))
                if elem.tag == '{{{0}}}recursion'.format(CLUFTER_NS):
                    up = elem
                    walk = []
                    while up != ret:
                        walk.append(up.getparent().index(up))
                        up = up.getparent()
                    #walk = reversed(tuple(walk))  # XXX reversed, dangerous?
                    walk.reverse()
                    walk = tuple(walk)
                    at = elem.attrib.get('at', '*')
                    prev = hooks.setdefault(at, walk)
                    if prev is not walk:
                        raise FilterError(None, "Ambigous match for `{0}'"
                                          " tag ({1} vs {2})".format(at, walk, prev))

            log.debug("hooks {0}".format(hooks))
            return (ret, hooks)
        elif callable(sym):
            return sym
        else:
            log.debug("preprocess XSLT traverse symbols: skipping {0}"
                      .format(name))
            return None

    @classmethod
    def proceed_xslt(cls, in_obj, **kwargs):
        """Apply iteratively XSLT snippets as per the schema tree (walk)"""
        # XXX postprocess: omitted as standard defines the only root element

        def proceed(transformer, elem, children):
            if not callable(transformer):
                # expect (xslt, hooks)
                return do_proceed(transformer, elem, children)
            return transformer(elem, children)

        def do_proceed(xslt, elem, children):
            # in bottom-up manner
            snippet = deepcopy(xslt[0])  # in-situ template manipulation
            hooks = xslt[1]
            scheduled = OrderedDict()  # XXX to keep the law and order
            for _, c_elem in etree.iterwalk(elem, events=('start',)):
                if c_elem is elem:
                    continue
                if c_elem in children:
                    c_up = c_elem
                    while not c_up.tag in hooks and c_up.getparent() != elem:
                        c_up = c_up.getparent()
                    if c_up.tag in hooks or '*' in hooks:
                        target_tag = c_up.tag if c_up.tag in hooks else '*'
                        l = scheduled.setdefault(hooks[target_tag], [])
                        l.append(children[c_elem].getroot())
            for index_history, substitutes in scheduled.iteritems():
                #inserted = False
                tag = reduce(lambda x, y: x[y], index_history, snippet)
                parent = tag.getparent()
                #index = parent.index(tag)

                for s in substitutes:
                    #assert s.tag == "{{{0}}}snippet".format(CLUFTER_NS)
                    if s.tag == "{{{0}}}snippet".format(CLUFTER_NS):
                        # only single root "detached" supported (first == last)
                        dst = parent
                        dst.attrib.update(dict(s.attrib))
                        dst.extend(s)
                    else:
                        parent.append(s)

            cl = snippet.xpath("//clufter:recursion",
                                 namespaces={'clufter': CLUFTER_NS})
            if len(cl):
                log.info("Not all tags from clufter namespace used")
                # remove these remnants so cleanup_namespaces works well
                for e in cl:
                    e.getparent().remove(e)

            # xslt
            xslt_root = etree.Element('{{{0}}}stylesheet'.format(XSL_NS),
                                      version="1.0")
            top = filter(lambda x: x.tag in TOP_LEVEL_XSL, snippet)
            for e in top:
                print "e", etree.tostring(e)
                xslt_root.append(e)
            if len(snippet):
                log.debug("snippet {0}".format(etree.tostring(snippet)))
                template = etree.Element('{{{0}}}template'.format(XSL_NS),
                                         match=elem.tag)
                template.append(snippet) # XXX was extend
                xslt_root.append(template)
                print "ee", etree.tostring(xslt_root)
            #else:
            #    # we dont't apply if there is nothing local and not at root
            #    print "zdrham", elem.tag
            #    return elem

            elem = etree.ElementTree(elem)  # XXX not getroottree?
            log.debug("Applying {0}, {1}".format(type(elem), etree.tostring(elem)))
            log.debug("Applying on {0}".format(etree.tostring(xslt_root)))
            #ret = elem.xslt(xslt_root)
            xslt = etree.XSLT(xslt_root)
            ret = xslt(elem)
            #etree.cleanup_namespaces(ret)

            return ret

        def postprocess(ret):
            assert len(ret) == 1
            ret = ret[0]
            log.debug("Applying postprocess onto {0}".format(etree.tostring(ret)))
            if ret.getroot().tag == "{{{0}}}snippet".format(CLUFTER_NS):
                ret = ret.getroot()[0]
            # XXX: ugly solution to get rid of the unneeded namespace
            # (cleanup_namespaces did not work here)
            ret = etree.fromstring(etree.tostring(ret))
            etree.cleanup_namespaces(ret)
            return ret

        kwargs.update(preprocess=cls._xslt_preprocess, proceed=proceed,
                           postprocess=postprocess, sparse=True)
        return cls.proceed(in_obj, **kwargs)

    @classmethod
    def _xslt_template(cls, walk):
        """Generate (try to) complete XSLT template from the sparse snippets"""
        scheduled_walk = [walk]
        scheduled_subst = OrderedDict()
        ret = []
        while len(scheduled_walk):
            cur_walk = scheduled_walk.pop()
            for key, (transformer, children) in cur_walk.iteritems():
                scheduled_walk.append(children)
                if transformer is None or callable(transformer):
                    if callable(transformer):
                        log.warn("Cannot generate complete XSLT when callable"
                                 " present")
                    if key in scheduled_subst:
                        for tag in scheduled_subst.pop(key)[:]:
                            for child_tag in children.iterkeys():
                                l = scheduled_subst.setdefault(child_tag, [])
                                l.append(tag)
                    continue

                snippet = deepcopy(transformer[0])  # in-situ manipulation

                xslt_root = etree.Element('{{{0}}}stylesheet'.format(XSL_NS),
                                          version="1.0")
                top = filter(lambda x: x.tag in TOP_LEVEL_XSL, snippet)
                for e in top:
                    xslt_root.append(e)
                if len(snippet):
                    snippet.tag = '{{{0}}}template'.format(XSL_NS)
                    snippet.attrib['match'] = key
                    xslt_root.append(snippet)

                hooks = transformer[1]
                if not key in scheduled_subst:
                    if cur_walk is walk:
                        ret.append(xslt_root)
                    else:
                        raise FilterError(cls, "XSLT inconsistency 1")
                # in parallel: 1?
                if key in scheduled_subst:
                    for tag in scheduled_subst.pop(key):
                        e = etree.Element('{http://www.w3.org/1999/XSL/Transform}apply-templates',
                                          select=".//{0}".format(key))
                        parent = tag.getparent()
                        parent[parent.index(tag)] = e
                        ret[-1].append(snippet)
                # in parallel: 2?
                for target_tag, index_history in hooks.iteritems():
                    tag = reduce(lambda x, y: x[y], index_history, snippet)
                    l = scheduled_subst.setdefault(target_tag, [])
                    l.append(tag)

        assert not len(scheduled_subst)  # XXX either fail or remove forcibly
        map(lambda x: etree.cleanup_namespaces(x), ret)
        ret = map(lambda x: x, ret)

        return (lambda x: x[0] if len(x) == 1 else x)(ret)

    @classmethod
    def proceed(cls, in_obj, root_dir=DEFAULT_ROOT_DIR, **kwargs):
        """Push-button to be called from the filter itself"""
        d = dict(symbol=cls.name)
        d.update(kwargs)
        walk = in_obj.walk_schema(root_dir, **filtervarspop(d, (
                                  'symbol', 'sparse')))
        return cls._traverse(in_obj, walk, **d)

    @classmethod
    def proceed_xslt_filter(cls, in_obj, **kwargs):
        """Push-button to be called from the filter itself (with walk_default)"""
        # identity transform
        kwargs['walk_default'] = ""
        return cls.proceed_xslt(in_obj, **kwargs)

    @classmethod
    def get_template(cls, in_obj, root_dir=DEFAULT_ROOT_DIR, **kwargs):
        """Generate the overall XSLT template"""
        d = dict(symbol=cls.name)
        d.update(kwargs)
        walk = in_obj.walk_schema(root_dir, preprocess=cls._xslt_preprocess,
                                  sparse=False, **filtervarspop(d, ('symbol',)))
        return cls._xslt_template(walk)
