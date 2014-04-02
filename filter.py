# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base filter stuff (metaclass, decorator, etc.)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from os.path import dirname, join
from copy import deepcopy
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from lxml import etree

from .error import ClufterError
from .plugin_registry import MetaPlugin, PluginRegistry
from .utils import cli_undecor, \
                   head_tail, \
                   hybridproperty, \
                   filtervarspop
from .command_context import CommandContext

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
    'strip-space',
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
          call = start conversion
    """
    __metaclass__ = filters

    def __init__(self, in_format, out_format):
        self._in_format, self._out_format = in_format, out_format  # resolved

    @hybridproperty
    def in_format(this):
        """Input format identifier/class for the filter"""
        return this._in_format

    @hybridproperty
    def out_format(this):
        """Output format identifier/class for the filter"""
        return this._out_format

    def __call__(self, in_obj, flt_ctxt=None, **kwargs):
        """Default is to use a function decorated with `deco`"""
        if flt_ctxt is None:  # when estranged (not under Command control)
            cmd_ctxt = CommandContext()
            flt_ctxt = cmd_ctxt.ensure_filter(self)
        outdecl = self._fnc(flt_ctxt, in_obj, **kwargs)
        outdecl_head, outdecl_tail = head_tail(outdecl)
        return self.out_format(outdecl_head, *outdecl_tail)

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


class XMLFilter(Filter, MetaPlugin):

    xslt_identity = '''\
    <xsl:template match="{0}@*|{0}node()" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
       </xsl:copy>
    </xsl:template>'''

    @staticmethod
    def _traverse(in_fmt, walk, et=None,
                  walk_default_first=None, walk_default=None,
                  preprocess=lambda s, n, r: s, proceed=lambda *x: x,
                  postprocess=lambda x: x[0] if len(x) == 1 else x):
        """Generic traverse through XML as per symbols within schema tree"""
        tree_stack = [('', (None, walk), OrderedDict())]
        default = walk_default_first
        default = default if default is not None else walk_default
        skip_until = []
        if default is None:
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
                if elem.tag in tree_stack[-1][1][1] or default is not None:
                    if elem.tag not in tree_stack[-1][1][1]:
                        log.debug("Pushed to use default for `{0}'"
                                  .format(elem.tag))
                        previous = tree_stack[-1][1][1].copy()
                        tree_stack[-1][1][1].clear()
                        tree_stack[-1][1][1][elem.tag] = (default, previous)
                    walk_new_sym, walk_new_rest = tree_stack[-1][1][1][elem.tag]
                    default = walk_default  # for the rest under first/root
                    walk_new_sym = preprocess(walk_new_sym, elem.tag,
                                              tree_stack[-1][1][0])
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
        # XXX can be [] in case of not finding anything, should we emit error?
        #     addendum: sometimes comments (top-level only?) will cause this
        return postprocess(ret)

    @staticmethod
    def _xslt_preprocess(sym, name, parent=None):
        """Preprocessing of schema tree XSLT snippets to real (sub)templates

        If callable is observed instead of XSLT snippet, keep it untouched.
        Used by `proceed_xslt` and `get_template` methods (hence class-wide).
        """
        # in top-down manner
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

            log.debug("walking {0}".format(etree.tostring(ret)))
            will_mix = 0  # whether any descent-mix observed
            for event, elem in etree.iterwalk(ret, events=('start', )):
                # XXX xpath/specific tag filter
                # register each recurse point at the tag required
                # so it can be utilized in bottom-up pairing (from
                # particular definitions to where it is expected)

                # not needed
                #if elem is ret:
                #    continue
                log.debug("Got {0}".format(elem.tag))
                if elem.tag in ('{{{0}}}descent'.format(CLUFTER_NS),
                                '{{{0}}}descent-mix'.format(CLUFTER_NS)):
                    up = elem
                    walk = []
                    while up != ret:
                        walk.append(up.getparent().index(up))
                        up = up.getparent()
                    #walk = reversed(tuple(walk))  # XXX reversed, dangerous?
                    walk.reverse()
                    walk = tuple(walk)
                    mix = elem.tag == '{{{0}}}descent-mix'.format(CLUFTER_NS)
                    mix += mix and \
                            elem.attrib.get('preserve-rest', "false") == "true"
                    will_mix = max(will_mix, mix)
                    at = elem.attrib.get('at', '*')
                    # XXX can be a|b|c
                    prev = hooks.setdefault(at, (walk, mix))
                    if prev != (walk, mix):
                        raise FilterError(None, "Ambigous match for `{0}'"
                                          " tag ({1} vs {2})".format(at, walk, prev))

            # do_mix decides whether the current sub-template will be
            # be applied and the result attached (0), or just merged
            # to the parent template (1 if not preserve-rest required,
            # 2 otherwise)
            do_mix = parent[1].get(name, parent[1].get('*', (None, None)))[1] \
                     if parent else 0
            if do_mix is None:
                raise RuntimeError("Parent does not expect `{0}' nor wildcard"
                                   .format(name))
            if do_mix and do_mix < will_mix:
                raise RuntimeError("Parent does not want preserve-rest while"
                                   " children wants to")
            elif do_mix > 1 and will_mix:
                do_mix = 1

            #if len(ret) and parent:
            #    top = filter(lambda x: x.tag in TOP_LEVEL_XSL, ret)
            #    for e in top:
            #        toplevel.append(e)
            #        ret.remove(e)

            # note that when do_mix, nested top_levels are actually propagated
            # back, which is the inverse of what we are doing here
            if parent and isinstance(parent[0], etree._Element) and not do_mix:
                top = filter(lambda x: x.tag in TOP_LEVEL_XSL, parent[0])
                for e in top:
                    #print "at", sym, "appending", etree.tostring(e)
                    ret.append(deepcopy(e))
                #for e in toplevel:
                #    parent[0].append(e)

            log.debug("hooks {0}".format(hooks))
            return (ret, hooks, do_mix)
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

        def _merge_previous(snippet, hooks, elem, children):
            # snippet, an original preprocessed "piece of template puzzle",
            # has some of its subelements substituted as per hooks that
            # together with elem traversal and children dict decides which
            # parts (of previously proceeded symbols) will be grabbed
            scheduled = OrderedDict()  # XXX to keep the law and order
            for _, c_elem in etree.iterwalk(elem, events=('start',)):
                if c_elem is elem:
                    continue
                if c_elem in children:
                    c_up = c_elem
                    while not c_up.tag in hooks and c_up.getparent() != elem:
                        c_up = c_up.getparent()
                    target_tag = c_up.tag if c_up.tag in hooks else '*'
                    if c_up.tag in hooks or '*' in hooks:
                        l = scheduled.setdefault(hooks[target_tag], [])
                        l.append(children[c_elem].getroot())

            for (index_history, mix), substitutes in scheduled.iteritems():
                tag = reduce(lambda x, y: x[y], index_history, snippet)
                parent = tag.getparent()
                index = parent.index(tag)

                for s in substitutes:
                    #assert s.tag == "{{{0}}}snippet".format(CLUFTER_NS)
                    log.debug("before extension: {0}".format(etree.tostring(s)))
                    if s.tag == "{{{0}}}snippet".format(CLUFTER_NS):
                        # only single root "detached" supported (first == last)
                        dst = parent
                        dst.attrib.update(dict(s.attrib))
                        #dst[index:index] = s
                        tag.extend(s)
                    elif mix:
                        tag.extend(s)
                    else:
                        # required by obfuscate
                        tag.append(s)
                    log.debug("as extended contains: {0}".format(etree.tostring(tag)))

            cl = snippet.xpath("//clufter:descent|//clufter:descent-mix",
                                 namespaces={'clufter': CLUFTER_NS})
            # remove these remnants so cleanup_namespaces works well
            for e in cl:
                parent = e.getparent()
                index = parent.index(e)
                parent[index:index] = e.getchildren()
                e.getparent().remove(e)

        def do_proceed(xslt, elem, children):
            # in bottom-up manner

            hooks, do_mix = xslt[1:]
            # something already "mixed", shortcut, if first "mix" copy+clear
            if not len(xslt[0]):
                assert do_mix
                return xslt[0].getroottree()

            snippet = deepcopy(xslt[0])  # for in-situ template manipulation

            if do_mix:
                xslt[0].clear()  # if we mix, it is only once

            _merge_previous(snippet, hooks, elem, children)

            # XSLT to either be performed (do_mix == 0) or remembered (>0)
            xslt_root = etree.Element('{{{0}}}stylesheet'.format(XSL_NS),
                                      version="1.0")
            # move top-level items directly to the stylesheet being built
            if do_mix:
                xslt_root.text = snippet.text
            for e in filter(lambda x: x.tag in TOP_LEVEL_XSL
                                   or x.tag is etree.Comment, snippet):
                xslt_root.append(e)

            # if something still remains, we assume it is "template"
            if len(snippet):
                log.debug("snippet0: {0}, {1}, {2}".format(do_mix, elem.tag, etree.tostring(snippet)))
                #if not filter(lambda x: x.tag in TOP_LEVEL_XSL, snippet):
                template = etree.Element('{{{0}}}template'.format(XSL_NS),
                                         match=elem.tag)
                if do_mix:
                    template.extend(snippet)
                else:
                    template.append(snippet)
                log.debug("template1: {0}".format(etree.tostring(template)))
                #snippet.append(template)
                ##else:
                ##    template = snippet
                # ^ XXX was extend
                xslt_root.append(template)
                #print "ee", etree.tostring(xslt_root)

            # append "identities" to preserve application
            # XXX needs clarification
            if do_mix == 1:
                template = etree.XML(cls.xslt_identity.format(elem.tag + '/'))
            elif elem.getparent() is None:
            #elif elem.getparent() is None and not do_mix:
                template = etree.XML(cls.xslt_identity.format(''))
                xslt_root.append(template)

            #else:
            #    # we dont't apply if there is nothing local and not at root
            #    print "zdrham", elem.tag
            #    return elem

            if do_mix:
                # "mix/carry" case in which we postpone this XSLT execution
                # (presumably non-local) by enquing it to the parent's turn
                #ret = xslt_root.getroot()
                ret = etree.ElementTree(xslt_root)
            else:
                # "eager" case in which we perform the (presumably local)
                # XSLT execution immediately
                elem = etree.ElementTree(elem)  # XXX not getroottree?
                log.debug("Applying {0}, {1}".format(type(elem), etree.tostring(elem)))
                log.debug("Applying on {0}".format(etree.tostring(xslt_root)))
                #ret = elem.xslt(xslt_root)
                xslt = etree.XSLT(xslt_root)
                ret = xslt(elem)
                # following seems to carefully preserve space (depending on
                # xsl:output)
                #ret = etree.fromstring(str(xslt(elem))).getroottree()
                log.debug("With result {0}".format(etree.tostring(ret)))
                #etree.cleanup_namespaces(ret)
            return ret

        def postprocess(ret):
            #log.debug("Applying postprocess onto {0}".format(etree.tostring(ret)))
            assert len(ret) == 1
            ret = ret[0]
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

    # XXX missing descent-mix
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
                for target_tag, (index_history, mix) in hooks.iteritems():
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
        d = dict(symbol=cli_undecor(cls.name))
        d.update(kwargs)
        walk = in_obj.walk_schema(root_dir, **filtervarspop(d, (
                                  'symbol', 'sparse')))
        return cls._traverse(in_obj, walk, **d)

    @classmethod
    def proceed_xslt_filter(cls, in_obj, **kwargs):
        """Push-button to be called from the filter itself (with walk_default)"""
        # XXX identity transform
        kwargs['walk_default_first'] = '<clufter:descent-mix preserve-rest="true"/>'
        return cls.proceed_xslt(in_obj, **kwargs)

    @classmethod
    def get_template(cls, in_obj, root_dir=DEFAULT_ROOT_DIR, **kwargs):
        """Generate the overall XSLT template"""
        d = dict(symbol=cli_undecor(cls.name))
        d.update(kwargs)
        walk = in_obj.walk_schema(root_dir, preprocess=cls._xslt_preprocess,
                                  sparse=False, **filtervarspop(d, ('symbol',)))
        return cls._xslt_template(walk)
