# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Setup script/data"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

try:
    from setuptools import setup, Extension
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Extension

from collections import Callable
from glob import glob
from os import getcwd, getenv, sep, walk
from os.path import (join as path_join, basename as path_basename,
                     dirname as path_dirname, normpath as path_norm,
                     isabs as path_isabs, isdir as path_isdir,
                     isfile as path_isfile, splitext as path_splitext)
from shutil import copy, copymode
from sys import prefix as sys_prefix

from distutils.cmd import Command
from distutils.errors import DistutilsSetupError
from distutils.command.build import build
from distutils.command.build_ext import build_ext
from distutils.command.install_data import install_data
from setuptools.command.develop import develop as setuptools_develop
# otherwise fails on
#   error: option --single-version-externally-managed not recognized...managed
# with default pip install
from setuptools.command.install import install as setuptools_install

# bail out if any code is not valid (http://stackoverflow.com/a/2240549)
import py_compile
orig_py_compile = py_compile.compile
def doraise_py_compile(file, cfile=None, dfile=None, doraise=False):
    orig_py_compile(file, cfile=cfile, dfile=dfile, doraise=True)
py_compile.compile = doraise_py_compile

PREFER_GITHUB=True
DEBUG = getenv("SETUPDEBUG")
DBGPFX = str(__file__)

#
# Custom machinery extending setuptools/distutils with mechanism
# for parameterization (mainly paths) and even content of these files
#

true_gen = lambda this: True
# XXX copy-paste of utils_func.py
bifilter = \
    lambda fnc, seq: \
        reduce(lambda acc, x: acc[int(not fnc(x))].append(x) or acc,
               seq, ([], []))

# this is needed to workaround naive approach in recent setuptools
# (https://bitbucket.org/pypa/setuptools/issue/195/no-longer-follows-symbolic)
# which follows symlinks but cannot prune the excluded dirs (perhaps
# declared so as to prevent infinite symlink recursion at the first place!)
# directly at the point of unfolding the directory tree traversal further
def find_packages(where=None, exclude=()):
    ret = []
    if not where:
        where = getcwd()
    excl_set = set(e.strip('*.') for e in exclude)  # rough overapproximation!
    for root, dirs, files in walk(where, followlinks=True):
        assert '.' not in root
        pkg_root = root[len(where):].lstrip(sep).replace(sep, '.')
        dirs[:] = [d for d in dirs
                   if d not in excl_set
                   and '.' not in d
                   and path_isfile(path_join(root, d, '__init__.py'))]
        ret.extend('.'.join((pkg_root, d)).lstrip('.') for d in dirs)
    return ret


# http://code.activestate.com/recipes/502261-python-distutils-pkg-config/#c1
def pkgconfig(*packages, **kw):
    try:
        from subprocess import check_output
        getoutput = lambda cmd: check_output(cmd, shell=True)
    except ImportError:
        from commands import getoutput
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in getoutput("pkg-config --libs --cflags {0}"
                           .format(' '.join(packages))).split():
        if token[:2] in flag_map:
            kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else:  # throw others to extra_link_args
            kw.setdefault('extra_link_args', []).append(token)
    for k, v in kw.iteritems():  # remove duplicates
        kw[k] = list(set(v))
    return kw

# inspired from speaklater: http://pypi.python.org/pypi/speaklater
class LazyRead(object):
    """Mimic string that in fact is read on-demand from file(s)

    Note: only direct use, str methods and '+' operator supported.
    """
    def __init__(self, filename, postproc=lambda c: c):
        self._filename = filename
        self._postproc = postproc
        self._content = None
    @property
    def content(self):
        ret = self._content
        if ret is None:
            with open(self._filename) as f:
                ret = self._content = self._postproc(f.read())
        return ret
    def __str__(self):           return str(self.content)
    def __repr__(self):          return repr(self.content)
    def __getattr__(self, what): return getattr(self.content, what)
    def __add__(self, other):    return self.content + other
    def __radd__(self, other):   return other + self.content


class Binary(Extension):
    pass


class build_binary(build_ext):
    @staticmethod
    def prereq(self):
        #return any(isinstance(e, Binary)
        #           for e in self.distribution.ext_modules)
        mine = self.distribution.get_option_dict(build_binary.__name__)
        return bool(mine.get('binaries', ()))

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.binaries = ()

    def finalize_options(self):
        build_ext.finalize_options(self)
        self.extensions = self.binaries
        self.build_lib = path_dirname(self.build_lib)
        #self.extensions, self.distribution.ext_modules = bifilter(
        #    lambda e: isinstance(e, Binary), self.distribution.ext_modules
        #)

    def build_extensions(self):
        compiler = self.compiler
        compiler.link_shared_object = \
            lambda *args, **kwargs: \
                compiler.link_executable(
                    *args, **dict((k, v) for k, v in kwargs.iteritems()
                                  if k not in ('export_symbols', 'build_temp'))
                )

        build_ext.build_extensions(self)

    def check_extensions_list(self, extensions):
        if not all(isinstance(i, Binary) for i in extensions):
            raise DistutilsSetupError("Only Binary instances allowed")

    def get_ext_filename(self, ext_name):
        return path_splitext(build_ext.get_ext_filename(self, ext_name))[0]


class develop(setuptools_develop):
    def install_for_development(self):
        self.reinitialize_command('pkg_prepare', develop=1)
        self.run_command('pkg_prepare')


class install(setuptools_install):
     def finalize_options(self):
        self.single_version_externally_managed = True
        orig_root = self.root  # avoid original install fail on SVEM + not root
        if not orig_root:
            self.root = sep
        setuptools_install.finalize_options(self)
        self.root = orig_root


class install_data(install_data):
    # Change predicate telling whether to run ``install_data''
    # subcommand within ``install'' command to always return true
    prereq = staticmethod(true_gen)


def setup_pkg_prepare(pkg_name, pkg_prepare_options=()):

    class pkg_prepare(Command):
        DEV_SWITCH = 'develop'
        BUILD_DEV_SWITCH = 'build_develop'
        description = ("Prepare specified files, i.e. substitute some values "
                       "(works as a subcommand for ``build'' and ``install'' "
                       "and can also mimic enhanced ``develop'' using %s)"
                       % DEV_SWITCH)
        user_options = [
            (key.replace('_', '-') + "=", None, "specify " + help
             + " for " + pkg_name) for key, help in pkg_prepare_options
        ]
        user_options.append((DEV_SWITCH.replace('_', '-'), None,
                             "mimics ``develop'' command "
                             "(to be used only w/ standalone ``pkg_prepare'')"))
        user_options.append((BUILD_DEV_SWITCH.replace('_', '-'), None,
                             "as --{0} but quit early "
                             "(to be used only w/ standalone ``pkg_prepare'')"
                             .format(DEV_SWITCH)))
        boolean_options = (DEV_SWITCH, BUILD_DEV_SWITCH)
        needs_any_opt = ('package_data', 'data_files',
                         'buildonly_files', 'built_files')
        needs_always_opts = ('pkg_params', )

        @classmethod
        def inject_cmdclass(cls, *new_classes, **orig_classes):
            cmdclass = {}
            for name, injectclass in orig_classes.iteritems():
                cmdclass[name], new = cls._inject(name, injectclass)
                new_classes += new
            for c in (cls, ) + new_classes:
                cmdclass[c.__name__] = c
            return cmdclass

        @classmethod
        def _inject(cls, name, orig_cls):
            sub_cmds = (cls, )
            if hasattr(orig_cls, '__iter__'):
                orig_cls, sub_cmds = (lambda c, *s: (c, sub_cmds + s))(*orig_cls)
            sub_cmd_names = set(s.__name__ for s in sub_cmds)
            orig_sub_commands = [s for s in orig_cls.sub_commands
                                 if s[0] not in sub_cmd_names]

            class new_cls(orig_cls):
                sub_commands = [(sub_cmd.__name__, getattr(sub_cmd, 'prereq',
                                                           true_gen))
                                for sub_cmd in sub_cmds] + orig_sub_commands
                description = (orig_cls.description + " (modified: "
                               "additionally prepare some files for %s, "
                               "i.e. substitute some values)" % pkg_name)
            new_cls.__name__ = orig_cls.__name__

            return new_cls, sub_cmds

        @staticmethod
        def prereq(self):
            """When is reasonable to run this (sub)command"""
            return (
                len(set(pkg_prepare.needs_any_opt).intersection(
                    self.distribution.get_option_dict(pkg_prepare.__name__)
                )) != 0
                and len(set(pkg_prepare.needs_always_opts).difference(
                    self.distribution.get_option_dict(pkg_prepare.__name__)
                )) == 0
            )

        def __init__(self, dist):
            self.pkg_options = tuple(
                key.split('=', 1)[0].replace('-', '_')
                for (key, _, __) in self.user_options
            )
            Command.__init__(self, dist)

        def initialize_options(self):
            # Parameters we want to obtain via setup.cfg, command-line
            # arguments etc. must be prepared as attributes of this object
            if DEBUG: print (DBGPFX + "\tinitialize_options")
            for key in (self.pkg_options + self.needs_any_opt
                        + self.needs_always_opts):
                setattr(self, key, None)
            setattr(self, self.DEV_SWITCH, 0)
            setattr(self, self.BUILD_DEV_SWITCH, 0)

        def finalize_options(self):
            # Obtained parameters are all moved to ``self.pkg_params'' dict
            if DEBUG: print (DBGPFX + "\tfinalize_options")
            for key in self.pkg_options:
                value = getattr(self, key)
                if value is None:
                    raise DistutilsSetupError \
                          ("Missing `%s' value (specify it on command-line"
                           " or in setup.cfg)" % key)
                else:
                    self.pkg_params[key] = value
            # Evaluate all functions within pkg_params (semi-lazy evaluation)
            for key, value in self.pkg_params.iteritems():
                if hasattr(value, "__call__") or isinstance(value, Callable):
                    self.pkg_params[key] = value(self.pkg_params)
            dist = self.distribution
            dist.data_files = dist.data_files or []
            dist.package_data = dist.package_data or {}
            self.buildonly_files = self.buildonly_files or ()
            self.built_files = self.built_files or ()

        def get_outputs(self):
            return ()  # called from install command for each subcommand

        def run(self):
            if DEBUG: print (DBGPFX + "\trun")
            if getattr(self, self.DEV_SWITCH, 0) \
            or getattr(self, self.BUILD_DEV_SWITCH, 0):
                # Mimic ``develop'' command over "prepared" files
                if DEBUG: print (DBGPFX + "\trun: mimic develop")
                self._pkg_prepare_build()
                self.run_command('build_binary')
                self.run_command('build_ext')
                if getattr(self, self.BUILD_DEV_SWITCH, 0):
                    return
                self._pkg_prepare_install()
                self.run_command('install_data')
                self.run_command('setuptools_develop')
                return
            if self.distribution.get_command_obj('build', create=False):
                # As a part of ``build'' command
                if DEBUG: print (DBGPFX + "\trun: build")
                self._pkg_prepare_build()
            if self.distribution.get_command_obj('install', create=False):
                # As a part of ``install'' command
                if DEBUG: print (DBGPFX + "\trun: install")
                self._pkg_prepare_install()
            else:
                from distutils import log
                log.debug("``pkg_name'' command used with no effect")

        def _pkg_prepare_build(self):
            for pkg_name, filedefs in (self.package_data or {}).iteritems():
                dst_top = self.distribution.package_dir.get('', '')
                dst_pkg = path_join(
                              dst_top,
                              self.distribution.package_dir.get(pkg_name, pkg_name)
                )
                if DEBUG: print (DBGPFX + "\tbuild dst_pkg %s" % dst_pkg)
                for filedef in filedefs:
                    self._pkg_prepare_file(
                        self.pkg_params[filedef['src']],
                        path_join(dst_pkg, self.pkg_params[filedef['dst']]),
                        filedef.get('substitute', False)
                    )
                    self.distribution.package_data[pkg_name].append(
                        self.pkg_params[filedef['dst']]
                    )
            for filedef in (self.data_files + self.buildonly_files):
                src_basename = path_basename(self.pkg_params[filedef['src']])
                dst_basename = path_basename(self.pkg_params[filedef['dst']])
                substitute = filedef.get('substitute', False)
                if all(c not in src_basename for c in '?*'):
                    if src_basename != dst_basename or substitute:
                        self._pkg_prepare_file(
                            self.pkg_params[filedef['src']],
                            path_join(
                                path_dirname(self.pkg_params[filedef['src']]),
                                dst_basename
                            ),
                            substitute
                        )
                else:
                    assert not substitute

        def _pkg_prepare_install(self):
            build_lib = self.get_finalized_command('build_binary').build_lib
            # two-staged copy in case of built_files
            for filedef in self.built_files:
                src = src_orig = self.pkg_params[filedef['src']]
                src = path_basename(src_orig)
                assert src == src_orig, "built_files contains dirs"
                src = path_join(build_lib, src)
                dst = self.pkg_params[filedef['dst']]
                dst = path_join(build_lib, path_basename(dst))
                if src != dst:
                    self._pkg_prepare_file(src, dst)
                self.pkg_params[filedef['src']] = dst
            icmd = self.distribution.get_command_obj('install', create=False)
            for filedef in (self.data_files + self.built_files):
                src = self.pkg_params[filedef['src']]
                dst = self.pkg_params[filedef['dst']]
                no_glob = all(c not in path_basename(src) for c in '?*')
                if dst.startswith(sys_prefix):
                    dst = path_join(icmd.install_base, dst[len(sys_prefix)+1:])
                self.distribution.data_files.append((
                    path_dirname(dst), [
                        path_join(
                            path_dirname(src),
                            path_basename(dst)
                        ),
                    ]
                ) if no_glob else (
                    dst,
                    glob(src)
                ))
                if DEBUG:
                    print (DBGPFX + "\tinstall data_files: %s"
                           % self.distribution.data_files)

        def _pkg_prepare_file(self, src, dst, substitution=False):
            if path_isabs(dst):
                # This function should not attempt doing dangerous things
                # and absolute file destination path is not expected anyway
                # (copying to destination paths is handled by ``install'')
                raise DistutilsSetupError \
                      ("Unexpected attempt to copy file %s to absolute"
                       " location %s" % (src, dst))
            if substitution:
                if DEBUG:
                    print (DBGPFX + "\tSubstituting strings while copying %s -> %s"
                           % (src, dst))
                if self.dry_run:
                    return
                try:
                    with open(src, "r") as fr:
                        with open(dst, "w") as fw:
                            content=fr.read()
                            for key in filter(
                                lambda k: not k.startswith("_")
                                          and k not in self.boolean_options,
                                self.pkg_params.iterkeys()
                            ):
                                if DEBUG:
                                    print (DBGPFX + "\tReplace %s -> %s"
                                           % ('@' + key.upper() + '@', self.pkg_params[key]))
                                content = content.replace(
                                              '@' + key.upper() + '@',
                                              self.pkg_params[key]
                                )
                            fw.write(content)
                    copymode(src, dst)
                except IOError, e:
                    raise DistutilsSetupError(str(e))
            else:
                if DEBUG:
                    print (DBGPFX + "\tSimply copying %s -> %s" % (src, dst))
                if self.dry_run:
                    return
                try:
                    copy(src, dst)
                    copymode(src, dst)
                except IOError, e:
                    raise DistutilsSetupError(str(e))
    # class pkg_prepare

    return pkg_prepare


# =========================================================================

self_discovery_plan = ['__project__']
while True:
    pkg = {}
    project = self_discovery_plan.pop()
    try:
        # XXX check relative import
        pkg = __import__(project, globals=pkg, level=1)
        break
    except ImportError:
        if project == '__project__':
            from glob import iglob
            self_discovery_plan.extend(p[:-len('.egg-info')].split('-', 1)[0]
                                       for p in iglob('*.egg-info'))
        if not self_discovery_plan:
            print "Cannot find myself, please help me with __project__ symlink"
            raise
#pkg_root = path_real('__project__')
pkg_name = pkg.package_name()

# Setup of ``pkg_prepare'' subcommand provided with the items to form options
# for this command;
# each such option requires to be specified (either via command-line or via
# setup.cfg) for correct invocation of this subcommand and after these
# specifications are proceeded, resulting (key, defined value) pairs are added
# into ``pkg_params'' passed as an option to this command in ``setup()''
# so they can be used for string substitutions as well
pkg_prepare = setup_pkg_prepare(pkg_name, (
    ('ccs_flatten',     "location of bundled helper ccs_flatten"),
    ('editor',          "which editor to use if EDITOR env variable not set"),
    ('hashalgo',       "which hash algorithm to use to generate output name"),
    ('ra_metadata_dir', "location of RGManager agents/metadata"),
    ('ra_metadata_ext', "extension used for RGManager agents' metadata"),
))

# Contains important values that are then referred to from ``package_data'',
# ``data_files'' etc. definitions within options for ``pkg_prepare'' subcommand
# in ``setup()'', and also serve for strings substituations/interpolations
# (applied to files defined within options for ``pkg_prepare'' subcommand where
# required and except for those starting with underscore)
#
# The right side can be either string or lazily evaluated function returning
# string with this dictionary (dynamically updated with the concrete values
# for parameters passed into ``setup_pkg_prepare'') as a parameter
pkg_param_defaults = 'defaults.py.in'
pkg_params = {
    '__ccs_flatten'        : 'ccs_flatten',
    '__ra_metadata'        : lambda pkg_params:
                             path_norm('ccs-flatten/*.'
                                       + pkg_params['ra_metadata_ext']),
    '__ccs_flatten_config' : path_norm("ccs-flatten/config.h.in"),
    'ccs_flatten_config'   : path_norm("ccs-flatten/config.h"),
    '__defaults'           : path_join(pkg_name, pkg_param_defaults),
    'defaults'             : path_join(pkg_name, 'defaults.py'),
}


# =========================================================================


def cond_require(package, *packages, **preferred):
    packages = (lambda *args: args)(package, *packages)
    for package in packages:
        for preferred_package, sym in preferred.iteritems():
            try:
                preferred_module = __import__(preferred_package)
                for symbol in ((sym, ) if isinstance(sym, basestring) else sym):
                    if not hasattr(preferred_module, symbol):
                        raise ImportError
            except ImportError:
                return (package, )
    return ()

url_dict = dict(name=pkg_name, ver=pkg.version)
if PREFER_GITHUB:
    url = 'https://github.com/jnpkrn/{name}'
    download_url = url + '/tarball/v{ver}'
else:
    url = 'http://people.redhat.com/jpokorny/pkgs/{name}'
    download_url = url + '/{name}-{ver}.tar.gz'
download_url = download_url if '-' not in pkg.version else ''

setup(

    # STANDARD DISTUTILS ARGUMENTS

    name=pkg_name,
    version=pkg.version,
    description=pkg.description_text(justhead=True),
    url=url.format(**url_dict),
    license=pkg.license,
    author=pkg.author_text(justname=True),
    author_email=pkg.author_text(justname=False),
    #maintainer=pkg.author.partition(", ")[0],
    #maintainer_email=pkg.email.partition(", ")[0],
    download_url=download_url.format(**url_dict),
    #long_description=pkg.description_text(justhead=False),
    long_description=LazyRead('README', lambda c: c.rstrip('\n')),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Clustering',
        'Topic :: System :: Systems Administration',
    ),
    keywords='cluster filter framework XML XSLT',

    # ``find_packages'' provided by setuptools avoids the unconvenient
    # listing each subpackage in package hierarchy
    packages=find_packages(
        exclude=('ez_setup', '__project__', '__project__.*', '*.tests'),
    ) + ['.'.join(lib.split(sep)) for lib in
         filter(path_isdir,
                glob(path_join(pkg_name, 'ext-plugins', 'lib-*', '*')))
    ],
    # Following content is also duplicated (in a simplier/more declarative way)
    # in MANIFEST.in which serves for ``setup.py sdist'' command and is
    # necessary due to http://bugs.python.org/issue2279 fixed as of Python 2.7;
    # TODO: MANIFEST.in will be presumably dropped at some point in the future
    # Note: See ``package_data'' under options['pkg_prepare']
    package_data={
        pkg_name: [
            pkg_param_defaults,
            'formats/*/*.rng',
            'ext-plugins/PURPOSE',
        ],
    },
    # Note: See ``data_files'' in options for ``pkg_prepare'' subcommand
    #data_files=(),
    # Override ``build'' command handler with local specialized one
    cmdclass = pkg_prepare.inject_cmdclass(
        develop,
        build=(build, build_binary),
        install=(install, install_data),
        setuptools_develop=setuptools_develop,
    ),
    options = {
        # Options "passed" to ``pkg_prepare'' subcommand
        pkg_prepare.__name__: dict(
            pkg_params=pkg_params,
            built_files=(
                dict(src='__ccs_flatten', dst='ccs_flatten'),
            ),
            # In addition to standard ``data_files''
            data_files=(
                dict(src='__ra_metadata', dst='ra_metadata_dir'),
            ),
            # Similar to ``data files'' but for files used e.g. for building
            # C extensions
            buildonly_files=(
                dict(src='__ccs_flatten_config', dst='ccs_flatten_config', substitute=True),
                dict(src='__defaults',           dst='defaults',           substitute=True),
            ),

        ),
        build_binary.__name__: dict(
            binaries=(
                Binary(pkg_params['__ccs_flatten'],
                    sources=[path_join('ccs-flatten', f) for f in
                             ('flatten.c',
                              'reslist.c',
                              'resrules.c',
                              'restree.c',
                              'xmlconf.c')],
                    **pkgconfig('libxml-2.0')
                ),
            ),
        ),
    },


    # ADDITIONAL SETUPTOOLS ARGUMENTS

    setup_requires=(
    ),
    install_requires=(
        'lxml',
    ) + cond_require('ordereddict', collections='OrderedDict'),
    # Use pure ``package_data'' value (i.e. do no use MANIFEST.ini or CVS tree);
    # see also comment by ``package data''
    include_package_data=False,

    extras_require={
        'test': cond_require('unittest2', unittest='runner')
    },

    # TODO: uncomment this when ready for tests
    test_suite='{0}.tests'.format(pkg_name),
    tests_require=cond_require('unittest2', unittest='runner'),

    entry_points = {
        'console_scripts': (
            '{0} = {0}.__main__'.format(pkg_name),
        ),
    },
)
