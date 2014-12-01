# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base filter stuff (metaclass, decorator, etc.)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from copy import deepcopy
from os import environ, isatty, stat
from os.path import dirname, join
from shlex import split as shlex_split
from shutil import rmtree
from subprocess import CalledProcessError, check_call
from sys import modules, stderr, __stdin__
from tempfile import mkdtemp, NamedTemporaryFile
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from lxml import etree

from . import package_name
from .error import ClufterError, ClufterPlainError
from .format import CompositeFormat, XML
from .plugin_registry import MetaPlugin, PluginRegistry
from .utils import args2tuple, \
                   filterdict_keep, filterdict_pop, \
                   head_tail, hybridproperty, \
                   tuplist
from .utils_func import apply_preserving_depth, \
                        apply_aggregation_preserving_depth, \
                        apply_intercalate, \
                        loose_zip, \
                        zip_empty
from .utils_prog import cli_undecor, which
from .utils_xml import CLUFTER_NS, XSL_NS, \
                       namespaced, nselem, squote, element_juggler, \
                       xml_get_root_pi, xmltag_get_namespace
from .utils_xslt import xslt_identity
from .command_context import CommandContext

try:
    from .defaults import EDITOR
except ImportError:
    EDITOR = ''
EDITOR = environ.get('EDITOR', EDITOR)

log = logging.getLogger(__name__)

DEFAULT_ROOT_DIR = join(dirname(__file__), 'filters')

# XXX: consult standard/books
_TOP_LEVEL_XSL = (
    'attribute-set',
    'import',
    'include',
    'key',
    'namespace-alias',
    'output',
    'param',
    'strip-space',
    'template',
    'variable',
)

# requires context implying "weak, not a strong/standalone expression"
_IMPLIED_TOP_LEVEL_XSL = (
    'when',
)
TOP_LEVEL_XSL = [namespaced(XSL_NS, e) for e in
                 _TOP_LEVEL_XSL + _IMPLIED_TOP_LEVEL_XSL]


class FilterError(ClufterError):
    pass


class FilterPlainError(ClufterPlainError, FilterError):
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

    @staticmethod
    def _resolve_formats_composite(formats):
        # XXX should rather be implemented by CompositeFormat itself?
        composite_onthefly = \
            lambda protocol, *args: \
                CompositeFormat(protocol, formats=formats, *args)
        # XXX currently instantiation only (no match for composite classes)
        composite_onthefly.as_instance = composite_onthefly
        composite_onthefly.context = CompositeFormat.context
        return composite_onthefly

    @classmethod
    def _resolve_formats(cls, formats):
        res_input = [cls.in_format, cls.out_format]
        res_output = apply_preserving_depth(formats.get)(res_input)
        if apply_aggregation_preserving_depth(all)(res_output):
            log.debug("Resolve at `{0}' filter: `{1}' -> {2}"
                      .format(cls.name, repr(res_input), repr(res_output)))
            # capture composite formats if present;  when running
            # into composite format, we replace in-situ the whole iterable
            # with as-of-now resolved formats with lazily pulled
            # CompositeFormat passing it these formats along the standard
            # business (as opposed to on-the-fly class creation when it
            # probably won't be ever instantiated anyway);
            # extra lambda wrapping so as to surely make a closure around
            # ("remember correctly") the current value of res_output
            res_output = tuple(
                cls._resolve_formats_composite(o) if tuplist(o) else o
                for o in res_output
            )
            return res_output
        # drop the filter if cannot resolve any of the formats
        res_input = apply_intercalate(res_input)
        map(lambda (i, x): log.warning("Resolve at `{0}' filter:"
                                       " `{1}' (#{2}) format fail"
                                       .format(cls.name, res_input[i], i)),
            filter(lambda (i, x): not(x),
                   enumerate(apply_intercalate(res_output))))
        return None

    def __new__(cls, formats):
        io_formats = cls._resolve_formats(formats)
        if io_formats is None:
            return None
        self = super(Filter, cls).__new__(cls)
        self._in_format, self._out_format = io_formats
        return self

    @hybridproperty
    def in_format(this):
        """Input format identifier/class for the filter"""
        return this._in_format

    @hybridproperty
    def out_format(this):
        """Output format identifier/class for the filter"""
        return this._out_format

    def __call__(self, in_obj, flt_ctxt=None, **fmt_kws):
        """Default is to use a function decorated with `deco`"""
        if flt_ctxt is None:  # when estranged (not under Command control)
            cmd_ctxt = CommandContext()
            flt_ctxt = cmd_ctxt.ensure_filter(self)
        outdecl = self._fnc(flt_ctxt, in_obj)
        outdecl_head, outdecl_tail = head_tail(outdecl)
        fmt_kws = filterdict_keep(flt_ctxt, *self.out_format.context, **fmt_kws)
        return self.out_format(outdecl_head, *outdecl_tail, **fmt_kws)

    @classmethod
    def deco(cls, in_format, out_format):
        """Decorator as an easy factory of actual filters"""
        def deco_fnc(fnc):
            log.debug("Filter: deco for {0}".format(fnc))
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
    """Base for XML/XSLT traversal filters"""

    _in_format = _out_format = 'XML'

    @staticmethod
    def command_common(cmd_ctxt,
                       nocheck=False,
                       batch=False,
                       editor=EDITOR,
                       raw=False):
        """\
            nocheck   do not validate any step (even if self-checks present)
            batch     do not interact (validation failure recovery, etc.)
            editor    customize editor to run (unused in batch mode)
            raw       do not care about pretty-printed output
        """
        flt_ctxt = cmd_ctxt.filter()
        flt_ctxt.setdefault('validator_specs', {'': ''} if nocheck else {},
                            bypass=True)
        flt_ctxt.update(
            raw=raw,
            interactive=not(batch and isatty(__stdin__.fileno())),
            editor=editor
        )

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
                    try:
                        log.debug("Proceeded {0}".format(
                                  etree.tostring(tree_stack[-1][2][elem]).replace('\n', '')))
                    except AttributeError:
                        log.debug("Proceeded {0}".format(tree_stack[-1][2][elem]))

                # XXX: optimization prunning, probably no good
                #else:
                #    skip_until = [('end', tree_stack[-1][0])]
                #    log.debug("Skipping (C) until: {0}".format(skip_until))

        ret = tree_stack[-1][2].values()
        # XXX can be [] in case of not finding anything, should we emit error?
        #     addendum: sometimes comments (top-level only?) will cause this
        return postprocess(ret)

    @classmethod
    def _try_edit(cls, res_snippet, schema_path, schema_snippet, msgs,
                  use_offset=True, editor=''):
        editor = editor.strip() or EDITOR
        pkg_name = package_name()
        message = [
            "{0} manual validation failure recovery due to (local positions):",
            "",
            "{1}",
            "",
            "On the basis of the two snippets enclosed in (XML PI) separators",
            "revealing the purpose, to-be-fixed invalid result and excerpt of",
            "{2}",
            "(validating schema), the situation can be resolved by either:",
            "",
            ". realizing and FIXING the issue (and possibly notifying {0}",
            "  maintainer): directly EDIT the respective snippet (upon",
            "  exiting the editor, the snippet will be inspected again)",
            ". OMITTING the snippet from the result, but be warned, this",
            "  may cause validation error at the level closer to the root",
            ". TERMINATING the whole conversion: DELETE everything",
            "",
            "+ forcing the snippet, empty or not, without validation:",
            "  TURN `:force-this=false` to `:force-this=true`",
            "+ forcing the whole block of snippets without validation:",
            "  CHANGE `force-block` attribute in the root element to `true`",
        ]
        offset = len(message) + len(msgs) + 5 if use_offset else 0
        e = '\n  '.join(["[{0}:{1}] {2}".format(m[0] + offset, *m[1:])
                        for m in msgs])
        message = '  ' + '\n  '.join(message).format(pkg_name, e, schema_path)
        prompt = """\
<{0}-recovery force-block="false">

<?{0} message
{1}
?>

<?{0} EDIT-result-snippet-start:force-this=false?>
{2}
<?{0} EDIT-result-snippet-end?>

<?{0} NOEDIT-schema-snippet-start?>
{3}
<?{0} NOEDIT-schema-snippet-end?>

</{0}-recovery>
""".format(pkg_name, message, res_snippet, schema_snippet)
        tmpdir = mkdtemp(prefix=pkg_name)
        reply, force = '', ''
        try:
            tmp = NamedTemporaryFile(dir=tmpdir, suffix='.xml', delete=True)
            with tmp as tmpfile:
                tmpfile.write(prompt)
                tmpfile.flush()
                orig_mtime = stat(tmp.name).st_mtime
                # XXX: Windows platform: delete=False, then close-popen-open
                editor_args = shlex_split(editor) + [tmp.name]
                assert len(editor_args) >= 2
                editor_args[0] = which(editor_args[0])
                log.info("running `{0}'".format(' '.join(editor_args)))
                try:
                    # pty.spawn doesn't work as nicely
                    with open('/dev/tty') as f_tty:
                        check_call(editor_args, stdin=f_tty)
                except (CalledProcessError, IOError) as e:
                    raise FilterError(cls, str(e))
                except OSError:
                    raise FilterError(cls, "Editor `{0}' seems unavailable"
                                            .format(editor))
                if orig_mtime == stat(tmp.name).st_mtime:
                    return None, force  # no change occurred
                tmpfile.seek(0)
                reply = tmpfile.read().strip()
        finally:
            rmtree(tmpdir)
        if not reply:
            return False, force  # terminating
        elems = []
        reply = etree.fromstring(reply)
        if reply.attrib.get('force-block', '').lower() == 'true':
            force = 'block'
        for root_pi in xml_get_root_pi(reply):
            if (root_pi.target == pkg_name
            and root_pi.text.strip().startswith('EDIT-result-snippet-start')):
                text = root_pi.text[len('EDIT-result-snippet-start') + 1:]
                attrs = dict(a.strip().split('=') for a in text.split(':'))
                if attrs.get('force-this', 'false').lower() == 'true':
                    force = force or 'this'
                for sibling in root_pi.itersiblings():
                    if isinstance(sibling, type(root_pi)):
                        break
                    elems.append(sibling)
                break
        return elems, force

    @classmethod
    def _xslt_get_validate_hook(cls, validator, interactive=True, **kws):
        assert validator is not None

        def validate_hook(ret):
            global_msgs, single_elem, pkg_name = [], False, package_name()
            pi_comment = pkg_name + '-comment'

            # figure out the target element, skip if not any suitable
            if ret:
                # "protected" comments have to be turned to something
                # else, here a processing instruction
                cl = ret.xpath("//clufter:comment",
                               namespaces={'clufter': CLUFTER_NS})
                for e in cl:
                    element_juggler.rebind(etree.PI(pi_comment, e.text),
                                           element_juggler.grab(e))
                    element_juggler.drop(e)
                #to_check = (ret.getroot(), )
                root = ret.getroot()
                if root.tag == namespaced(CLUFTER_NS, "snippet"):
                    to_check = reversed(root)
                else:
                    to_check = (root, )
                    single_elem = True
            else:
                to_check = ()
            worklist = list(i for i in to_check
                            if xmltag_get_namespace(i.tag) != XSL_NS)
            use_offset = True
            while worklist:
                elem = worklist.pop()
                if elem is None:
                    use_offset = True
                    continue
                msgs, schema, schema_snippet = validator(elem, start=elem.tag)
                if not (msgs and schema and interactive):
                    global_msgs.extend(msgs)
                    break
                parent_pos = element_juggler.grab(elem)
                res_snippet = etree.tostring(elem, pretty_print=True)
                force = False
                while True:
                    try:
                        elems, force = cls._try_edit(res_snippet.strip(),
                                                     schema, schema_snippet,
                                                     msgs, use_offset, **kws)
                    except FilterError as e:
                        log.warning(str(e))
                        elems = ()
                    if elems is not None:  # active change
                        break
                if not elems:
                    element_juggler.drop(elem)
                    if elems is False:
                        print >>stderr, "Terminating"
                        raise SystemExit
                elif single_elem:
                    assert len(elems) == 1
                else:
                    # positive change occurred (reverse due to insert)
                    elems = reversed(elems)
                worklist.append(None)
                for e in elems:
                    if not force:
                        worklist.append(e)  # ensure revalidation
                    element_juggler.rebind(e, parent_pos)
                if force == 'block':
                    return ret, ()  # validation for the whole block cancelled
                use_offset = False

            cl = ret.xpath("//processing-instruction('{0}')".format(pi_comment))
            for e in cl:
                element_juggler.rebind(nselem(CLUFTER_NS, 'comment',
                                              e.text.strip().join((' ', ) * 2)),
                                       element_juggler.grab(e))
                element_juggler.drop(e)
            return ret, global_msgs
        return validate_hook

    def _xslt_get_atom_hook(self, quiet=False, validator_specs={}, **kws):
        validate_hook = None
        if issubclass(self._out_format, XML):
            # only when out format is XML-based, we can be quite sure the
            # resulting form/protocol is etree
            # XXX otherwise there would have to be a hint about it
            #     or alternatively it would be passed into the filters
            #     generically, which might hurt implicit laziness?
            spec = validator_specs.get('etree', validator_specs.get('', None))
            validator = self._out_format.validator('etree', spec=spec)
            if validator:
                validate_hook = self._xslt_get_validate_hook(validator, **kws)
        return (lambda ret, error_log=():
                    self._xslt_atom_hook(ret, error_log, quiet, validate_hook))

    @staticmethod
    def _xslt_atom_hook(ret, error_log, quiet=False, validate_hook=None):
        fatal = []
        for entry in error_log:
            msg = "XSLT: {0}".format(entry.message)
            if entry.type != 0 or not quiet:  # avoid logging (suppression)
                print >>stderr, msg
                if entry.type != 0:
                    fatal.append("XSLT: " + entry.message)
        if not fatal and validate_hook:
            ret, entries = validate_hook(ret)
            fatal.extend("RNG: " + ':'.join(args2tuple(str(e[0]), str(e[1]),
                                                       *e[2:]))
                         for e in entries)
        if fatal:
            raise FilterPlainError("FAIL: {0}".format((', ').join(e for e in fatal)))
        return ret

    @staticmethod
    def _xslt_preprocess(sym, name, parent=None):
        """Preprocessing of schema tree XSLT snippets to real (sub)templates

        If callable is observed instead of XSLT snippet, keep it untouched.
        Used by `proceed_xslt` and `get_template` methods (hence class-wide).

        ...also, turn xls:comment into clufter:comment form so as to preserve
        (hold off) emitting XML comments, that would eitherwise be dropped
        because of repeated XSLT processings (xsl:comment -> literal comment
                                              -> forgotten)
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
                if elem.tag in (namespaced(CLUFTER_NS, t) for t
                                in ('descent', 'descent-mix')):
                    up = elem
                    walk = []
                    while up != ret:
                        walk.append(up.getparent().index(up))
                        up = up.getparent()
                    #walk = reversed(tuple(walk))  # XXX reversed, dangerous?
                    walk.reverse()
                    walk = tuple(walk)
                    mix = elem.tag == namespaced(CLUFTER_NS, 'descent-mix')
                    mix += mix and \
                            elem.attrib.get('preserve-rest', "false") == "true"
                    will_mix = max(will_mix, mix)
                    at = elem.attrib.get('at', '*')
                    # XXX can be a|b|c
                    prev = hooks.setdefault(at, (walk, mix))
                    if prev != (walk, mix):
                        raise FilterError(None, "Ambigous match for `{0}'"
                                          " tag ({1} vs {2})".format(at, walk, prev))
                elif (elem.tag == namespaced(XSL_NS, 'comment')
                      and parent and not(parent[2])):
                    # in non-root, turn the comments into "protected" ones
                    element_juggler.rebind(
                        nselem(CLUFTER_NS, 'comment', elem.text, *tuple(elem)),
                        element_juggler.grab(elem)
                    )
                    element_juggler.drop(elem)

            if parent and parent[2] == 1 and '*' not in hooks:
                hooks['*'] = (len(ret), ), 1
                ret.append(nselem(CLUFTER_NS, 'descent-mix',
                                  attrib={'preserve-rest': 'false'}))

            # do_mix decides whether the current sub-template will be
            # be applied and the result attached (0), or just merged
            # to the parent template (1 if not preserve-rest required,
            # 2 otherwise)
            do_mix = parent[1].get(name, parent[1].get('*', (None, None)))[1] \
                     if parent else will_mix
            if do_mix is None:
                raise RuntimeError("Parent does not expect `{0}' nor wildcard"
                                   .format(name))
            if do_mix and do_mix < will_mix:
                raise RuntimeError("Parent does not want preserve-rest while"
                                   " child wants to")
            elif do_mix > 1 and will_mix:  # and not parent
                do_mix = 1

            #toplevel = []
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
    def proceed_xslt(cls, in_obj, xslt_atom_hook=lambda ret, err: ret, **kws):
        """Apply iteratively XSLT snippets as per the schema tree (walk)

        You should likely use `proceed_xslt_filter` wrapper instead.
        """
        # XXX postprocess: omitted as standard defines the only root element

        def proceed(transformer, elem, children):
            # expect (xslt, hooks) in the former case
            return xslt_atom_hook(*do_proceed(transformer, elem, children)
                                  if not callable(transformer)
                                  else transformer(elem, children))

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
                    #assert s.tag == namespaced(CLUFTER_NS, 'snippet')
                    log.debug("before extension: {0}".format(etree.tostring(s)))
                    if s.tag == namespaced(CLUFTER_NS, 'snippet'):
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
            error_log = ()
            # something already "mixed", shortcut, if first "mix" copy+clear
            if not len(xslt[0]):
                assert do_mix
                return xslt[0].getroottree(), error_log

            snippet = deepcopy(xslt[0])  # for in-situ template manipulation

            if do_mix:
                xslt[0].clear()  # if we mix, it is only once

            _merge_previous(snippet, hooks, elem, children)

            # XSLT to either be performed (do_mix == 0) or remembered (>0)
            xslt_root = nselem(XSL_NS, 'stylesheet', version="1.0")
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
                template = nselem(XSL_NS, 'template', match=elem.tag)
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
                if do_mix == 1 and elem.getparent() is not None:
                    e = nselem(XSL_NS, 'apply-templates',
                            select="*")
                    template.append(e)
            if do_mix > 1 or elem.getparent() is None and not children:
            # and not do_mix:
                template = etree.XML(xslt_identity(''))
                xslt_root.append(template)

            #else:
            #    # we dont't apply if there is nothing local and not at root
            #    print "zdrham", elem.tag
            #    return elem

            if do_mix and elem.getparent() is not None:
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
                error_log = xslt.error_log
                # following seems to carefully preserve space (depending on
                # xsl:output)
                #ret = etree.fromstring(str(xslt(elem))).getroottree()
                log.debug("With result {0}".format(etree.tostring(ret)))
                #etree.cleanup_namespaces(ret)
            return ret, error_log

        def postprocess(ret):
            """Postprocess the final result

            ...also, turn clufter:comment back into (now true) comment form
            """
            #log.debug("Applying postprocess onto {0}".format(etree.tostring(ret)))
            assert len(ret) == 1
            ret = ret[0]
            if ret.getroot().tag == namespaced(CLUFTER_NS, 'snippet'):
                ret = ret.getroot()[0]

            # any "protected" comments are turned into full-fledged ones now
            cl = ret.xpath("//clufter:comment",
                           namespaces={'clufter': CLUFTER_NS})
            for e in cl:
                element_juggler.rebind(etree.Comment(e.text),
                                       element_juggler.grab(e))
                element_juggler.drop(e)

            # XXX: ugly solution to get rid of the unneeded namespace
            # (cleanup_namespaces did not work here)
            ret = etree.fromstring(etree.tostring(ret))
            etree.cleanup_namespaces(ret)
            return ret

        if not kws.pop('textmode', False):
            kws.setdefault('postprocess', postprocess)
        defaults = dict(preprocess=cls._xslt_preprocess, proceed=proceed,
                        sparse=True)
        defaults.update(kws)
        return cls.proceed(in_obj, **defaults)

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
                        log.warning("Cannot generate complete XSLT when"
                                    " callable present")
                    if key in scheduled_subst:
                        for tag in scheduled_subst.pop(key)[:]:
                            for child_tag in children.iterkeys():
                                l = scheduled_subst.setdefault(child_tag, [])
                                l.append(tag)
                    continue

                snippet = deepcopy(transformer[0])  # in-situ manipulation

                xslt_root = nselem(XSL_NS, 'stylesheet', version="1.0")
                top = filter(lambda x: x.tag in TOP_LEVEL_XSL, snippet)
                for e in top:
                    xslt_root.append(e)
                if len(snippet):
                    snippet.tag = namespaced(XSL_NS, 'template')
                    snippet.attrib['match'] = key
                    xslt_root.append(snippet)

                hooks = transformer[1]
                if key not in scheduled_subst:
                    if cur_walk is walk:
                        ret.append(xslt_root)
                    else:
                        raise FilterError(cls, "XSLT inconsistency 1")
                # in parallel: 1?
                if key in scheduled_subst:
                    for tag in scheduled_subst.pop(key):
                        e = nselem(XSL_NS, 'apply-templates',
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
    def proceed(cls, in_obj, root_dir=None, **kwargs):
        """Push-button to be called from the filter itself"""
        if not root_dir:
            root_dir = dirname(modules[cls.__module__].__file__)
        kwargs.setdefault('symbol', cli_undecor(cls.name))
        walk = in_obj.walk_schema(root_dir, **filterdict_pop(kwargs, 'symbol',
                                                                     'sparse'))
        return cls._traverse(in_obj, walk, **kwargs)

    def filter_proceed_xslt(self, in_obj, **kwargs):
        """Push-button to be called from the filter itself, with walk_default"""
        raw, textmode = kwargs.pop('raw', False), kwargs.get('textmode', False)
        def_first, system = '', kwargs.pop('system', '')
        system_extra = kwargs.pop('system_extra', ())
        def_first += ('<xsl:param name="system" select="{0}"/>'
                      .format(squote(system)))
        if system:
            # guarantee at least 3 extra params, so they can be relied upon
            for i, val in loose_zip(xrange(1,4), system_extra):
                val = val if val is not zip_empty else ''
                def_first += ('<xsl:param name="system_{0}" select="{1}"/>'
                              .format(str(i), squote(val)))
        if textmode:
            def_first += '<xsl:output method="text"/>'
            def_first += '<xsl:strip-space elements="*"/>'
            def_first += '<clufter:descent-mix preserve-rest="false"/>'
        else:
            def_first += '<clufter:descent-mix preserve-rest="true"/>'

        xslt_atom_hook = self._xslt_get_atom_hook(**filterdict_pop(kwargs,
            'editor', 'interactive', 'quiet', 'validator_specs'
        ))

        kwargs.setdefault('walk_default_first', def_first)
        kwargs['xslt_atom_hook'] = xslt_atom_hook

        ret = self.proceed_xslt(in_obj, **kwargs)
        if not raw and not textmode:
            # <http://lxml.de/FAQ.html#
            #  why-doesn-t-the-pretty-print-option-reformat-my-xml-output>
            # XXX we could use a single shared un-blanking parser around
            parser = etree.XMLParser(remove_blank_text=True)
            ret = etree.fromstring(etree.tostring(ret), parser)
        elif textmode:
            ret = str(ret)
        return ret

    def ctxt_proceed_xslt(self, ctxt, in_obj, **kwargs):
        """The same as `filter_proceed_xslt`, context-aware"""
        kwargs = filterdict_keep(ctxt,
            'raw', 'system', 'system_extra',                   # proceed_xslt
            'editor', 'interactive', 'quiet', 'validator_specs',  # atom_hook
            **kwargs
        )
        return self.filter_proceed_xslt(in_obj, **kwargs)

    @classmethod
    def get_template(cls, in_obj, root_dir=None, **kwargs):
        """Generate the overall XSLT template"""
        if not root_dir:
            root_dir = dirname(modules[cls.__module__].__file__)
        kwargs.setdefault('symbol', cli_undecor(cls.name))
        walk = in_obj.walk_schema(root_dir, preprocess=cls._xslt_preprocess,
                                  sparse=False,
                                  **filterdict_pop(kwargs, 'symbol'))
        return cls._xslt_template(walk)
