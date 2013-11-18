# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Base format stuff (metaclass, classes, etc.)"""
__author__ = "Jan Pokorný <jpokorny at redhat dot com>"

# TODO: NamedTuple for tree_stack

import imp
import logging
from copy import deepcopy
from os import extsep, walk
from os.path import commonprefix, splitext, basename
from sys import modules

from lxml import etree

from .plugin_registry import PluginRegistry
from .utils import ClufterError, classproperty

log = logging.getLogger(__name__)
MAX_DEPTH = 1000


class FormatError(ClufterError):
    pass


class formats(PluginRegistry):
    """Format registry (to be used as a metaclass for formats)"""
    use_local = True

    def __init__(cls, name, bases, attrs):
        cls._protocols = {}
        # protocols merge: top-down through inheritance
        for base in reversed(cls.__bases__):
            if hasattr(base, '_protocols'):
                cls._protocols.update(base._protocols)
        # updated with locally defined protocols (marked by `producing` wrapper)
        for attr, obj in attrs.iteritems():
            if hasattr(obj, '_protocol'):
                cls._protocols.update(**{obj._protocol: obj})


def producing(protocol, protect=False):
    """Decorator for externalization method understood by the `formats` magic

    Caching of representations is a bonus."""
    def deco_meth(meth):
        def deco_args(self, protocol, protect_safe=False, *args):
            try:
                produced = self._representations[protocol]
            except KeyError:
                produced = meth(self, protocol, *args)
                # computed -> stored normalization: tuple nontupled or len == 1
                if not isinstance(produced, tuple) or len(produced) == 1:
                    produced = (produced, )
                self._representations[protocol] = produced

            # stored -> computed normalization: detuple if len == 1
            if isinstance(produced, tuple) and len(produced) == 1:
                produced = produced[0]
            if protect and not protect_safe:
                log.debug("{0}:{1}:Forced deepcopy of `{2}' instance"
                          .format(self.__class__.name, meth.__name__,
                                  type(produced).__name__))
                produced = deepcopy(produced)
            return produced

        setattr(deco_args, '_protocol', protocol)  # mark for later recognition
        return deco_args
    return deco_meth


class Format(object):
    """Base for configuration formats

    Base principles:
        - protocols: string label denoting how to int-/externalize
          - union of protocols within inheritance hierarchy and
            locally defined ones (prioritized)
            - to define one, add a method decorated with `@producing(<proto>)`
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
        prev = self._representations.setdefault(protocol, args)
        assert prev is args

    def produce(self, protocol, *args, **kwargs):
        """"Called by implicit invocation to get data externalized"""
        if protocol == 'native':
            protocol = self.native_protocol

        assert protocol in self._protocols
        return self._protocols[protocol](self, protocol, *args, **kwargs)

    def __init__(self, protocol, *args):
        """Format constructor, i.e., object = concrete internal data"""
        self._representations = {}
        self.swallow(protocol, *args)

    def __call__(self, protocol='native', *args, **kwargs):
        """Way to externalize object's internal data"""
        return self.produce(protocol, *args)

    @property
    def protocols(self):
        """Set of supported protocols for int-/externalization"""
        return self._protocols.copy()  # installed by meta-level

    @property
    def representations(self):
        """Mapping of `protocol: initializing_data`"""
        return self._representations.copy()

    ####

    native_protocol = 'bytestring'

    @producing('bytestring')
    def get_bytestring(self, protocol):
        if 'file' in self._representations:  # break the possible loop
            with file(self('file'), 'rb') as f:
                return f.read()

    @producing('file')
    def get_file(self, protocol, filename):
        with file(filename, 'wb') as f:
            f.write(self('bytestring'))
        return filename


class XML(Format):
    """"Base for XML-based configuration formats"""
    @classproperty
    def root(self):
        """Root tag of the XML document"""
        raise ValueError  # NotImplemented

    @classproperty
    def rng_schema(self):
        """Relax-ng schema for validation document"""
        return None

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

    @producing('bytestring')
    def get_bytestring(self, protocol):
        ret = super(XML, self).get_bytestring(self)
        if ret is not None:
            return ret

        # fallback
        return etree.tostring(self('etree', protect_safe=True),
                              pretty_print=True)

    @producing('etree', protect=True)
    def get_etree(self, protocol):
        return etree.fromstring(self('bytestring')).getroottree()
