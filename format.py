# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base format stuff (metaclass, classes, etc.)"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# TODO: NamedTuple for tree_stack

import imp
from copy import deepcopy
from glob import glob
from logging import getLogger
from os import extsep, fdopen, walk
from os.path import basename, commonprefix, dirname, exists, join, sep, splitext
from sys import modules, stdout
from warnings import warn

from lxml import etree

from .error import ClufterError
from .plugin_registry import MetaPlugin, PluginRegistry
from .utils import arg2wrapped, args2tuple, args2unwrapped, \
                   classproperty, \
                   mutable, \
                   tuplist
from .utils_xml import rng_pivot

log = getLogger(__name__)
MAX_DEPTH = 1000


class FormatError(ClufterError):
    pass


class formats(PluginRegistry):
    """Format registry (to be used as a metaclass for formats)"""
    def __init__(cls, name, bases, attrs):
        cls._protocols, cls._validators = {}, {}
        # protocols merge: top-down through inheritance
        for base in reversed(cls.__bases__):
            cls._protocols.update(getattr(base, '_protocols', {}))
            cls._validators.update(getattr(base, '_validators', {}))
        # updated with locally defined proto's (marked by `producing` wrapper)
        specs = attrs.get('validator_specs', {})

        for attr, obj in attrs.iteritems():
            try:
                protocol = obj._protocol
                delattr(obj, '_protocol')
                cls._protocols[protocol] = obj
                cls._validators[protocol] = obj._validator, None
                delattr(obj, '_validator')
            except AttributeError:
                pass

        for protocol in cls._protocols:
            newspec = specs.get(protocol, None)
            validator, spec = cls._validators.get(protocol, (None, ''))
            newspec = newspec if newspec is not None else spec
            if validator:
                cls._validators[protocol] = validator, newspec


class Format(object):
    """Base for configuration formats

    Base principles:
        - protocols: string label denoting how to int-/externalize
          - union of protocols within inheritance hierarchy and
            locally defined ones (prioritized)
            - to define one, add a method decorated with
              `@Format.producing(<proto>)`
            - be default, all such protocols are suitable for both
              int- and externalization, but you can prevent the latter
              context by raising an exception in the method body
        - create format instance = internalize, call = externalize
        - protocols are property of the class, representation of an instance


    Little bit of explanation:

                           FORMAT INSTANCE
                           (concrete data)
     INSTANTIATION    /-----------------------\       CALL        /--------
     (internalize)    | -protocols = set(...) |   (externalize)   | effect
    ----------------->| -representations =    |------------------>| and/or ...
    (protocol, *args) |   {protocol: (*args)} | (protocol, *args) |  value
           ^          \-----------------------/             ^     \--------
           |                                                |
           |                                                |
           +-- adds (protocol, *args) to representations,   |
               usually does nothing else (lazy approach)    |
                                                            |
             with each protocol there is a representation --+
             of concrete data associated,  either this or
             any other  that  can be promoted  (awakening
             from the previous laziness)  to the desired
             one is required

        Externalization methods are marked with `producing` decorator
        that takes protocol name as a parameter.

    """
    __metaclass__ = formats

    def swallow(self, protocol, *args):
        """"Called by implicit constructor to get a format instance"""
        if protocol == 'native':
            protocol = self.native_protocol

        assert protocol in self._protocols
        validator = self._validators.get(protocol, (None, ''))
        if validator[0] and validator[1]:
            ret, entries = validator[0](self, *args, spec=validator[1])
            if entries:
                raise FormatError(self,
                                  "Validation: {0}".format(', '.join(entries)))
        prev = self._representations.setdefault(protocol, args)
        assert prev is args

    def produce(self, protocol, *args, **kwargs):
        """"Called by implicit invocation to get data externalized"""
        if protocol == 'native':
            protocol = self.native_protocol

        assert protocol in self._protocols
        return self._protocols[protocol](self, protocol, *args, **kwargs)

    def __init__(self, protocol, *args, **kwargs):
        """Format constructor, i.e., object = concrete internal data"""
        self._representations = {}
        validator_specs = kwargs.pop('validator_specs', {})
        default = validator_specs.setdefault('', None)  # None ~ don't track
        for p in self._validators.iterkeys():
            spec = validator_specs.get(p, default)
            if spec is None:
                continue
            self._validators[p] = (self._validators[p][0], spec)
        # XXX self._dict = kwargs
        self.swallow(protocol, *args)

    @classmethod
    def as_instance(cls, *decl_or_instance):
        """Create an instance or verify and return existing one"""
        if decl_or_instance and isinstance(decl_or_instance[0], Format):
            instance = decl_or_instance[0]
            if not isinstance(instance, cls):
                raise FormatError(cls, "input object: format mismatch"
                                  " (expected `{0}', got `{1}')", cls.name,
                                  instance.__class__.name)
        else:
            instance = cls(*decl_or_instance)
        return instance

    def __call__(self, protocol='native', *args, **kwargs):
        """Way to externalize object's internal data"""
        return self.produce(protocol, *args, **kwargs)

    @property
    def protocols(self):
        """Set of supported protocols for int-/externalization"""
        return self._protocols.copy()  # installed by meta-level

    @property
    def representations(self):
        """Mapping of `protocol: initializing_data`"""
        return self._representations.copy()

    @staticmethod
    def producing(protocol, chained=False, protect=False, validator=None):
        """Decorator for externalizing method understood by the `Format` magic

        As a bonus: caching of representations."""
        def deco_meth(meth):
            def deco_args(self, protocol, *args, **kwargs):
                # XXX enforce nochain for this interative processing?
                protect_safe = kwargs.pop('protect_safe', False)
                try:
                    # stored -> computed norm.: detuple if len == 1
                    produced = args2unwrapped(*self._representations[protocol])
                except KeyError:
                    produced = None
                    worklist = [type(self)]
                    this_m = self._protocols[protocol]
                    while worklist:
                        t = worklist.pop()
                        that_m = t._protocols[protocol]
                        if that_m is this_m and chained:
                            worklist.extend(b for b in t.__bases__ if formats is
                                            getattr(b, '__metaclass__', None))
                            continue
                        if that_m is not this_m:
                            produced = that_m(self, protocol, *args, **kwargs)
                        if produced is None:
                            produced = meth(self, protocol, *args, **kwargs)
                            # computed -> stored normalization
                            self.swallow(protocol, *arg2wrapped(produced))

                if protect and not protect_safe and not mutable(produced):
                    log.debug("{0}:{1}:Forced deepcopy of `{2}' instance"
                              .format(self.__class__.name, meth.__name__,
                                      type(produced).__name__))
                    produced = deepcopy(produced)
                return produced

            deco_args.__name__, deco_args.__doc__ = meth.__name__, meth.__doc__
            deco_args._protocol = protocol  # mark for later recognition
            if validator:
                deco_args._validator = validator
            return deco_args
        return deco_meth

    ####

    @classproperty
    def native_protocol(self):
        """Native protocol"""
        raise AttributeError


class SimpleFormat(Format, MetaPlugin):
    """This is what most of the format classes want to subclass"""
    native_protocol = 'bytestring'

    def __init__(self, protocol, *args):
        """Format constructor, i.e., object = concrete uniformat data"""
        assert isinstance(protocol, basestring), \
               "protocol has to be string for `{0}', not `{1}'" \
               .format(self.__class__.__name__, protocol)
        super(SimpleFormat, self).__init__(protocol, *args)

    @Format.producing('bytestring')
    def get_bytestring(self, protocol):
        if 'file' in self._representations:  # break the possible loop
            with file(self('file'), 'rb') as f:
                return f.read()

    @Format.producing('file')
    def get_file(self, protocol, outfile):
        if hasattr(outfile, 'write'):
            # assume fileobj out of our control, do not close
            outfile.write(self('bytestring'))
            return outfile.name

        assert isinstance(outfile, basestring)
        if outfile == '-' or outfile.rstrip('0123456789') == '@':
            if outfile == '-':
                stdout.write(self('bytestring'))
            else:
                warn("@DIGIT+ in get_file deprecated, implicit handling fail?",
                     DeprecationWarning)
                with fdopen(int(outfile[1:]), 'ab') as f:
                    f.write(self('bytestring'))
        else:
            with file(outfile, 'wb') as f:
                f.write(self('bytestring'))
        return outfile

    @staticmethod
    def io_decl_fd(io_decl):
        """Return file descriptor (int) if conforms to "magic file" or None"""
        if tuplist(io_decl) and len(io_decl) >= 2 and io_decl[0] == 'file':
            if io_decl[1].rstrip('0123456789') == '@':
                return int(io_decl[1][1:])
        return None


class CompositeFormat(Format, MetaPlugin):
    """Quasi-format to stand in place of multiple formats at once

    It is intended to build on top of atomic formats (and only these,
    i.e., multi-level nesting is not supported as it doesn't bring
    any better handling anyway).

    Common format API is overridden so as to be performed per each
    contained/designated format in isolation, whereas the aggregated
    result is then returned.

    Note that the semantics implicitly require protocols prescribing
    the `CompositeFormat` instantiation to also become "composite",
    i.e., having form like ('composite', ('file', 'file')) instead
    of mere scalar like 'file' (IOW, whole declaration remains
    fully "typed").

    See also: Format, SimpleFormat
    """
    native_protocol = 'composite'  # to be overridden by per-instance one
                                   # XXX: hybridproperty?

    def __init__(self, protocol, *args, **kwargs):
        """Format constructor, i.e., object = concrete multiformat data

        Parameters:
            protocol    protocol, should match: ('composite', ('file', ...))
                        where 'file' is indeed variable
            args        each should represent arguments to be passed
                        into format instantiation for respective (order-wise)
                        protocol within the composite one
            kwargs      further keyword arguments; supported:
                        formats     iterable of format classes involved,
                                    matching the order of the "proper data
                                    part" within protocols
        """
        assert isinstance(protocol, tuple) and protocol \
               and protocol[0] == self.__class__.native_protocol, \
               "protocol has to be tuple initiated with {0} for {1}" \
               .format(self.__class__.native_protocol, self.__class__.__name__)
        formats = kwargs['formats']  # has to be present
        # further checks
        assert len(protocol) > 1
        assert tuplist(protocol[1]) and len(protocol[1]) > 1
        assert tuplist(formats) and len(protocol[1]) == len(formats)
        assert len(args) == len(formats)
        assert all(p in f._protocols for (f, p) in zip(formats, protocol[1]))
        self._protocols[protocol] = lambda *_: args  # just to pass the assert
        self.native_protocol = (self.__class__.native_protocol,
                                tuple(f.native_protocol for f in formats))
        # instantiate particular designated formats
        self._designee = tuple(
            f(p, *args2tuple(a))
            for (f, p, a) in zip(formats, protocol[1], args)
        )
        super(CompositeFormat, self).__init__(protocol, *args)

    def __iter__(self):
        return iter(self._designee)

    def __getitem__(self, index):
        return self._designee[index]

    def produce(self, protocol, *args, **kwargs):
        """"Called by implicit invocation to get data externalized"""
        if protocol == 'native':
            protocol = self.native_protocol

        assert tuplist(protocol) and len(protocol) > 1
        assert protocol[0] == self.__class__.native_protocol
        assert len(protocol[1]) == len(self._designee)
        args = args or ((),) * len(protocol[1])
        return tuple(f._protocols[p](f, p, *a, **kwargs)
                     for f, p, a in zip(self._designee, protocol[1], args))


class XML(SimpleFormat):
    """"Base for XML-based configuration formats"""
    @classproperty
    def root(self):
        """Root tag of the XML document"""
        raise AttributeError  # NotImplemented

    @staticmethod
    def _walk_schema_step_up(tree_stack):
        """Step up within the tree_stack (bottom-up return in dir structure)"""
        child_root, child_data = (lambda x, *y: (x, y))(*tree_stack.pop())
        log.debug("Moving upwards: `{0}' -> `{1}'"
                  .format(child_root, tree_stack[-1][0]))
        current_tracking = tree_stack[-1][2]
        if len(child_data[1]):
            name = basename(child_root)
            if name in current_tracking:
                to_update = current_tracking[name][1]
            else:
                to_update = current_tracking
            to_update.update(child_data[1])

        return current_tracking

    @staticmethod
    def _walk_schema_step_down(tree_stack, root):
        """Step down within the tree_stack (top-down diving in dir structure)

        Based on the fact that we traverse down by one level to already
        (shallowly) explored level so the item is already tracked at
        the parent and the shallow knowledge (dict) is passed down to be
        potentially extended -- as dict is mutable, this knowledge
        is shared between parent and child level.
        """
        log.debug("Moving downwards:`{0}' -> `{1}'"
                  .format(tree_stack[-1][0], root))
        tree_stack.append((root, None, {}))

        return tree_stack[-1][2]  # current tracking

    @classmethod
    def walk_schema(cls, root_dir, symbol=None, preprocess=lambda s, n: s,
                    sparse=True):
        """
        Get recipe for visiting symbol(s) within the XML as (sparsely) arranged

        Example of output::

            {
                'A': (<symbol>, {
                    'C': (<symbol>, {}),
                    'D': (<symbol>, {
                        'F': (<symbol>, {
                        })
                    })
                })
                'Z': (<symbol>, {})
            }

        NB: order of keys really does not matter.
        """
        xml_root = cls.root
        particular_namespace = '.'.join((cls.namespace, symbol or xml_root))
        result = {}
        tree_stack = [(root_dir, None, result)]  # for bottom-up reconstruction
        for root, dirs, files in walk(root_dir):
            # multi-step upwards and (followed by)/or single step downwards
            while commonprefix((root, tree_stack[-1][0])) != tree_stack[-1][0]:
                cls._walk_schema_step_up(tree_stack)
            if root != tree_stack[-1][0]:
                current_tracking = cls._walk_schema_step_down(tree_stack, root)
            else:
                assert root == root_dir
                # at root, we do not traverse to any other dir than `xml_root`
                map(lambda d: d != xml_root and dirs.remove(d), dirs[:])
                current_tracking = tree_stack[-1][2]
                files = []

            for i in dirs + files:
                name, ext = splitext(i)  # does not hurt even if it is a dir
                if name.startswith('_') or i in files and ext != extsep + 'py':
                    continue

                log.debug("Trying `{0}' at `{1}'".format(name, root))
                mfile, mpath, mdesc = imp.find_module(name, [root])
                # need to obfuscate the name due to, e.g., "logging" clash
                mname = '.'.join((particular_namespace, 'walk_' + name))
                # suppress problems with missing parent in module hierarchy
                modules.setdefault(particular_namespace, modules[__name__])
                if mname in modules:
                    mod = modules[mname]
                    if hasattr(mod, '__path__') and mod.__path__[0] != mpath:
                        # XXX robust?
                        raise FormatError(cls, "`{0}' already present"
                                          .format(mname))
                else:
                    try:
                        mod = imp.load_module(mname, mfile, mpath, mdesc)
                    except ImportError:
                        log.debug("Cannot load `{0}'".format(mpath))
                        continue
                    finally:
                        if mfile:
                            mfile.close()

                available = set(dir(mod)) - set(dir(type(mod)))
                swag = None
                if not symbol or symbol in available:
                    swag = getattr(mod, symbol) if symbol else tuple(available)
                    swag = preprocess(swag, name)
                if swag is None and (sparse or i in files):
                    continue  # files are terminals anyway
                current_tracking[name] = (swag, {})

        for i in xrange(MAX_DEPTH):
            if cls._walk_schema_step_up(tree_stack) is result:
                return result
        else:
            raise RuntimeError('INFLOOP detected')

    ###

    native_protocol = 'etree'
    validator_specs = {
        'etree': '*'  # grab whatever you'll find (with backtrack)
    }

    @classmethod
    def etree_rng_validator(cls, et, spec=validator_specs['etree'], start=None):
        # XXX holds its private cache under cls._validation_cache
        assert spec
        if not sep in spec:
            spec = join(dirname(__file__), 'formats', cls.root, spec)
        if any(filter(lambda c: c in spec, '?*')):
            globbed = glob(spec)
            spec = globbed or spec
        elif exists(spec):
            spec = args2tuple(spec)
        if not tuplist(spec):
            return et, ("Cannot validate, no matching spec: `{0}'"
                        .format(spec), )
        fatal = []
        for s in reversed(sorted(spec)):
            fatal[:] = []
            try:
                schema = cls._validation_cache.get(s, None)
            except AttributeError:
                setattr(cls, '_validation_cache', {})
                schema = None
            if schema is None:
                try:
                    cls._validation_cache[s] = schema = etree.RelaxNG(file=s)
                except etree.RelaxNGError:
                    log.warning("Problem processing RNG file `{0}'".format(s))
                    continue
            if start is not None:
                schema = rng_pivot(deepcopy(schema), start)
            try:
                schema.assertValid(et)
            except etree.DocumentInvalid:
                log.warning("Invalid as per RNG file `{0}'".format(s))
                for entry in schema.error_log:
                    fatal.append(entry.message)
            else:
                break
        else:
            log.warning("None of the validation attempts succeeded with"
                        " validator spec `{0}' ".format(spec))

        return et, fatal

    etree_validator = etree_rng_validator

    @SimpleFormat.producing('bytestring', chained=True)
    def get_bytestring(self, protocol):
        # chained fallback
        return etree.tostring(self('etree', protect_safe=True),
                              pretty_print=True)

    @SimpleFormat.producing('etree', protect=True,
                            validator=etree_validator.__func__)
    def get_etree(self, protocol):
        return etree.fromstring(self('bytestring')).getroottree()
