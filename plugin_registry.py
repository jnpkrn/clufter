# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Easy (at least for usage) plugin framework"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import imp
import logging
from os import extsep, walk
from os.path import abspath, dirname, join, splitext
from contextlib import contextmanager
from sys import modules

from .utils import classproperty, hybridproperty
from .utils_prog import cli_decor

log = logging.getLogger(__name__)


class MetaPlugin(object):
    """For use in the internal meta-hierarchy as "do not register me" mark"""


class PluginRegistry(type):
    """Core of simple plugin framework

    This ``superclass'' serves two roles:

    (1) metaclass for plugins (and its class hierarchy)
        - only a tiny wrapper on top of `type`

    (2) base class for particular registries

    Both roles are combined due to a very tight connection.

    Inspired by http://eli.thegreenplace.net/2012/08/07/ (Fundamental...).
    """
    _registries = set()  # dynamic tracking of specific registries

    #
    # these are relevant for use case (1)
    #

    # non-API

    def __new__(registry, name, bases, attrs):
        if '__metaclass__' not in attrs and MetaPlugin not in bases:
            # alleged end-use plugin
            ret = registry.probe(name, bases, attrs)
        else:
            if registry not in PluginRegistry._registries:
                log.debug("Registering `{0}' as registry"
                            .format(registry.registry))
                # specific registry not yet tracked
                # (e.g., specific plugin was imported natively)
                registry.setup()
                PluginRegistry._registries.add(registry)
                if registry.namespace not in modules:
                    # XXX hack to keep going in the test suite
                    __import__(registry.namespace)

            ret = super(PluginRegistry, registry).__new__(registry, name,
                                                          bases, attrs)

        return ret

    #
    # these are relevant for both (1) + (2)
    #

    @classmethod
    def probe(registry, name, bases, attrs):
        """Meta-magic to register plugin"""
        assert '-' not in name, "name cannot contain a dash"
        name = cli_decor(name)
        try:
            ret = registry._plugins[name]
            log.info("Probe `{0}' plugin under `{1}' registry: already tracked"
                     .format(name, registry.registry))
        except KeyError:
            log.debug("Probe `{0}' plugin under `{1}' registry: yet untracked"
                      .format(name, registry.registry))
            ret = super(PluginRegistry, registry).__new__(registry, name,
                                                          bases, attrs)
            registry._plugins[name] = ret
        finally:
            if registry._path_context is not None:
                registry._path_mapping[registry._path_context].add(name)

            return ret

    @hybridproperty
    def name(this):
        """Nicer access to __name__"""
        return this.__name__

    @classproperty
    def registry(registry):
        """Registry identifier"""
        return registry.__name__

    @classproperty
    def namespace(registry):
        """Absolute namespace possessed by the particular plugin registry

        For a plugin, this denotes to which registry/namespace it belongs.
        """
        try:
            return registry._namespace
        except AttributeError:
            registry._namespace = '.'.join((__package__, registry.__name__))
            return registry._namespace

    #
    # these are relevant for use case (2)
    #

    # non-API

    @classmethod
    @contextmanager
    def _path(registry, path):
        """Temporary path context setup enabling safe sideways use"""
        assert registry._path_context is None
        registry._path_context = path
        yield path, registry._path_mapping.setdefault(path, set())
        assert registry._path_context is not None
        registry._path_context = None

    @classmethod
    def _context(registry, paths):
        """Iterate through the paths yielding context along

        Context is a pair `(path, list_of_per_path_tracked_plugins_so_far)`.
        """
        if not isinstance(paths, (list, tuple)):
            if paths is None:
                return  # explictly asked not to use even implicit path
            paths = (paths, )

        # inject implicit one
        implicit = join(dirname(abspath(__file__)), registry.__name__)
        paths = (lambda *x: x)(implicit, *paths)

        for path in paths:
            with registry._path(path) as context:
                yield context

    # API

    @classmethod
    def setup(registry, reset=False):
        """Implicit setup upon first registry involvement or external reset"""
        attrs = ('_path_context', None), ('_path_mapping', {}), ('_plugins', {})
        if reset:
            map(lambda (a, d): setattr(registry, a, d), attrs)
        else:
            map(lambda (a, d): setattr(registry, a, getattr(registry, a, d)),
                attrs)
        if reset:
            PluginRegistry._registries.discard(registry)

    @classmethod
    def discover(registry, paths):
        """Find relevant plugins available at the specified path(s)

        Returns `{plugin_name: plugin_cls}` mapping of plugins found.
        """
        ret = {}
        for path, path_plugins in registry._context(paths):
            # skip if path already discovered (considered final)
            if not len(path_plugins):
                # visit *.py files within (and under) the path and probe them
                for root, dirs, files in walk(path):
                    for f in files:
                        name, ext = splitext(f)
                        if not name.startswith('_') and ext == extsep + 'py':
                            mfile, mpath, mdesc = imp.find_module(name, [root])
                            if not mfile:
                                log.debug("Omitting `{0}' at `{1}'"
                                          .format(name, root))
                                continue
                            mname = '.'.join((registry.namespace, name))
                            try:
                                imp.load_module(mname, mfile, mpath, mdesc)
                            finally:
                                mfile.close()
                path_plugins = registry._path_mapping[path]

            # filled as a side-effect of meta-magic, see `__new__`
            ret.update((n, registry._plugins[n]) for n in path_plugins)
            # add "built-in" ones
            ret.update((n, p) for n, p in registry._plugins.iteritems()
                       if MetaPlugin not in p.__bases__)

        return ret


class PluginManager(object):
    """Common (abstract) base for *Manager objects"""
    def __init__(self, *args, **kwargs):
        registry = kwargs.pop('registry', None) or self._default_registry
        self._registry = registry
        paths = kwargs.pop('paths', ())
        plugins = registry.discover(paths)
        plugins.update(kwargs.pop(registry.name if registry else '', {}))
        self._init_handle_plugins(plugins, *args, **kwargs)

    def _init_handle_plugins(self, plugins, *args, **kwargs):
        raise NotImplementedError('subclasses should implement')

    @property
    def registry(self):
        return self._registry
