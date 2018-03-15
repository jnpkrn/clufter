# distill-spec-prefix:   clufter, cl, fedora, python3_pkgversion, rhel, test
# distill-spec-requires: python2-devel [python3-devel]
#
# virtual provides:
#   clufter        -> clufter-cli
#   clufter-lib    -> python.+-clufter (any if multiple)
#   python-clufter -> python2-clufter (subject of change)
%{!?clufter_version: %global clufter_version  %{!?infer:0.77.2}%{?infer:%(
                                                python ../setup.py --version)}}
%{!?clufter_name:    %global clufter_name     %{!?infer:clufter}%{?infer:%(
                                                python ../setup.py --name)}}
%{!?clufter_license: %global clufter_license  %{!?infer:GPLv2+}%{?infer:%(
                                                python ../setup.py --license)}}

# special vars wrt. versioning
%{!?clufter_b:       %global clufter_b        1}
%global clufter_version_norm %(echo '%{clufter_version}' | tr '-' '_' \\
  | sed 's|\\([0-9]\\)a\\(_.*\\)\\?$|\\1|')
# http://fedoraproject.org/wiki/Packaging:NamingGuidelines#Pre-Release_packages
%global clufter_githash %(echo '%{clufter_version}' | tr '-' '_' \\
  | sed -n 's|.*[0-9]a_git\\.\\(.*\\)|\\1|p')
%global clufter_rel %(echo '%{clufter_githash}' \\
  | sed -n 'bS;:E;n;:S;s|\\(.\\+\\)|0.%{clufter_b}.a_\\1|p;tE;c\\%{clufter_b}')

%bcond_without pagure
%if 0%{defined:_with_pagure}
%global pagure 1
%endif

%if "%{clufter_version}" == "%{clufter_version_norm}"
%{!?clufter_source:  %global clufter_source   %{name}-%{version}}
%{!?clufter_check:   %global clufter_check    2}
%else
%{!?clufter_source:  %global clufter_source   %{name}-%{clufter_version}}
%{!?clufter_check:   %global clufter_check    1}
%endif
%{!?clufter_url_main:%global clufter_url_main %{!?pagure:https://github.com/jnpkrn/%{name}}%{?pagure:https://pagure.io/%{name}}}
%{!?clufter_url_raw: %global clufter_url_raw  %{!?pagure:https://raw.githubusercontent.com/jnpkrn/%{name}/}%{?pagure:https://pagure.io/%{name}/raw/}}
%{!?clufter_url_dist:%global clufter_url_dist %{!?pagure:https://people.redhat.com/jpokorny/pkgs/%{name}/}%{?pagure:https://pagure.io/releases/%{name}/}}
%{!?clufter_url_bugs:%global clufter_url_bugs %{!?pagure:https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora&component=%{name}&version=rawhide}%{?pagure:https://pagure.io/%{name}/issues}}

%{!?clufter_python3: %global clufter_python3  python%{?python3_pkgversion}%{!?python3_pkgversion:3}}
%{!?clufter_pylib2:  %{?__python2: %global clufter_pylib2   python2-%{name}}}
%{!?clufter_pylib3:  %{?__python3: %global clufter_pylib3   %{clufter_python3}-%{name}}}
%{!?clufter_bin:     %global clufter_bin      %{name}-bin}
%{!?clufter_common:  %global clufter_common   %{name}-common}
%{!?clufter_lib:     %global clufter_lib      %{name}-lib}

# Python package customizations
%{!?clufter_ccs_flatten:      %global clufter_ccs_flatten       %{_libexecdir}/%{clufter_source}/ccs_flatten}
%{!?clufter_editor:           %global clufter_editor            %{_bindir}/nano}
%{!?clufter_extplugins_shared:%global clufter_extplugins_shared %{_datarootdir}/%{name}/ext-plugins}
%{!?clufter_shell_posix:      %global clufter_shell_posix       %(which sh 2>/dev/null || echo /bin/SHELL-POSIX)}
%{!?clufter_shell_bashlike:   %global clufter_shell_bashlike    %(which bash 2>/dev/null || echo /bin/SHELL-BASHLIKE)}
%{!?clufter_ra_metadata_dir:  %global clufter_ra_metadata_dir   %{_datadir}/cluster}
%{!?clufter_ra_metadata_ext:  %global clufter_ra_metadata_ext   metadata}

%bcond_without script
%if %{with script}
  %bcond_without bashcomp
  %if %{with bashcomp}
    %bcond_without bashcomplink
  %endif
  %bcond_without manpage
%endif
%if %{with script}
  %{!?clufter_cli:     %global clufter_cli      %{name}-cli}
  %{!?clufter_script:  %global clufter_script   %{_bindir}/%{name}}
  %if %{with bashcomp}
    # may be overriden by pkg-config data of bash-completion
    %{!?clufter_bashcompdir:%global clufter_bashcompdir %{_datadir}/bash-completion/completions}
    %if %{with bashcomplink}
      %{!?clufter_bashcompreal:%global clufter_bashcompreal %{_sysconfdir}/%{name}/bash-completion}
    %else
      %undefine clufter_bashcompreal
    %endif
  %endif
  %if %{with manpage}
    %{!?clufter_manpagesec: %global clufter_manpagesec  1}
  %endif
%endif

%if 0%{?rhel} && 0%{?rhel} < 7
%bcond_with generated_schemas
%else
%bcond_without generated_schemas
%endif

# Preprocess the above specifications

%global clufter_sitelib    %{?clufter_pylib3:%{python3_sitelib}}%{!?clufter_pylib3:%{python2_sitelib}}/%{name}
%global clufter_setuptools %{?clufter_pylib3:%{clufter_python3}-setuptools}%{!?clufter_pylib3:python2-setuptools}
%global clufter_dopython   %{?clufter_pylib3:%{__python3}}%{!?__clufter_pylib3:%{?__python2}%{!?__python2:%{__python}}}
# for fedora, we are bound to release that introduced 3.2 since beginning
# (for python3-lxml this was the case since 14)
%if 0%{?clufter_pylib3:1} && 0%{?fedora} >= 15
%global clufter_pylib  %{clufter_pylib3}
%else
%if 0%{?clufter_pylib2:1}
%global clufter_pylib  %{clufter_pylib2}
%endif
%endif

# Improper specifications

%{!?clufter_pylib:%({error: need to build against at least one of Python 2 and 3}}

# universality++
# https://fedoraproject.org/wiki/EPEL:Packaging?rd=Packaging:EPEL#The_.25license_tag
%{!?_licensedir:%global license %doc}


Name:           %{clufter_name}
Version:        %{clufter_version_norm}
Release:        %{clufter_rel}%{?dist}
Group:          System Environment/Base
Summary:        Tool/library for transforming/analyzing cluster configuration formats
License:        %{clufter_license}
URL:            %{clufter_url_main}

# autosetup
BuildRequires:  git

# Python side (first item for pythonX* macros + overall Python run-time)
%if 0%{?clufter_pylib2:1}
BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
%if 0%{?clufter_check}
BuildRequires:  python2-lxml
%endif
%endif
%if 0%{?clufter_pylib3:1}
BuildRequires:  %{clufter_python3}-devel
BuildRequires:  %{clufter_python3}-setuptools
%if 0%{?clufter_check}
BuildRequires:  %{clufter_python3}-lxml
%endif
%endif

# following to ensure "which bash" (and, in extension, "which sh") works
BuildRequires:  bash which

# ccs_flatten helper
# ~ libxml2-devel
BuildRequires:  pkgconfig(libxml-2.0)

%if %{with generated_schemas}
# needed for schemadir path pointer
BuildRequires:  pkgconfig(pacemaker)
# needed for schemas themselves
BuildRequires:  pacemaker
# needed to squash multi-file schemas to single file
BuildRequires:  jing
# needed for xsltproc and xmllint respectively
BuildRequires:  libxslt libxml2
%endif

## global test_version 0.X.Y
%global testver %{?test_version}%{!?test_version:%{version}}

%if "%{clufter_version}" == "%{clufter_version_norm}"
Source0:        %{clufter_url_dist}%{name}-%{version}.tar.gz
%if 0%{?clufter_check} == 2
Source1:        %{clufter_url_dist}%{name}-%{testver}-tests.tar.xz
%endif
%else
Source0:        %{clufter_source}.tar.gz
# Source0 is created by Source1, just pass particular commit hash
# via GITHASH env. variable
Source1:        %{clufter_url_raw}%{clufter_githash}/%{?pagure:f/}misc/run-sdist-per-commit
%endif
%if %{with generated_schemas}
# Helpers in "borrow validation schemas from pacemaker installed along" process
Source2:        %{clufter_url_raw}%{clufter_githash}/%{?pagure:f/}misc/fix-jing-simplified-rng.xsl
Source3:        %{clufter_url_raw}%{clufter_githash}/%{?pagure:f/}misc/pacemaker-borrow-schemas
%endif


%global clufter_description %{!?infer:%(
cat <<EOF
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.
EOF)}%{?infer:%(../run-dev -h | sed '5,8p;d')}

%description
%{clufter_description}


%define pkgsimple() %(echo "%1" \\
  | sed -n 's|^%{name}-\\(.*\\)|\\1|p;tE;s|\\(.*\\)|-n \\1|p;:E')

%if %{with script}
%package %{pkgsimple %{clufter_cli}}
Group:          System Environment/Base
Summary:        Tool for transforming/analyzing cluster configuration formats
Provides:       %{name} = %{version}-%{release}
%if %{with bashcomp}
# for pkg-config file to be inspected during install phase
BuildRequires:  bash-completion
%endif
%if %{with manpage}
BuildRequires:  help2man
%endif
# following for pkg_resources module
Requires:       %{clufter_setuptools}
Requires:       %{clufter_pylib} = %{version}-%{release}
# "extras"
Requires:       %{clufter_editor}
BuildArch:      noarch

%description %{pkgsimple %{clufter_cli}}
%{clufter_description}

This package contains %{name} command-line interface for the underlying
library (packaged as %{clufter_pylib}).
%endif


%if 0%{?clufter_pylib2:1}
%package %{pkgsimple %{clufter_pylib2}}
Group:          System Environment/Libraries
Summary:        Library for transforming/analyzing cluster configuration formats
License:        %{clufter_license} and GFDL
Provides:       %{clufter_lib} = %{version}-%{release}
# legacy non-python-versioned business
%if 0%{?python_provide:1}
%{?python_provide:%python_provide %{clufter_pylib2}}
%else
%if %{clufter_pylib} == %{?clufter_pylib2}
Provides:       python-%{name} = %{version}-%{release}
Obsoletes:      python-%{name} < %{version}-%{release}
%endif
%endif
#implied-by#Requires: %%{clufter_ccs_flatten}
Requires:       %{clufter_bin} = %{version}-%{release}
#autodected# Requires:       libxml2
Requires:       python2-lxml
BuildArch:      noarch

%description %{pkgsimple %{clufter_pylib2}}
%{clufter_description}

This package contains %{name} library including built-in plugins.
%endif


%if 0%{?clufter_pylib3:1}
%package %{pkgsimple %{clufter_pylib3}}
Group:          System Environment/Libraries
Summary:        Library for transforming/analyzing cluster configuration formats
License:        %{clufter_license} and GFDL
Provides:       %{clufter_lib} = %{version}-%{release}
# legacy non-python-versioned business
%if 0%{?python_provide:1}
%{?python_provide:%python_provide %{clufter_pylib3}}
%endif
#implied-by#Requires: %%{clufter_ccs_flatten}
Requires:       %{clufter_bin} = %{version}-%{release}
#autodected# Requires:       libxml2
Requires:       %{clufter_python3}-lxml
BuildArch:      noarch

%description %{pkgsimple %{clufter_pylib3}}
%{clufter_description}

This package contains %{name} library including built-in plugins.
%endif


%package %{pkgsimple %{clufter_bin}}
Group:          System Environment/Libraries
Summary:        Common internal compiled files for %{name}
License:        %{clufter_license}
# for metadata
Requires:       %{clufter_common} = %{version}-%{release}

%description %{pkgsimple %{clufter_bin}}
%{clufter_description}

This package contains internal, arch-specific files for %{name}.


%package %{pkgsimple %{clufter_common}}
Group:          System Environment/Libraries
Summary:        Common internal data files for %{name}
License:        %{clufter_license}
BuildArch:      noarch

%description %{pkgsimple %{clufter_common}}
%{clufter_description}

This package contains internal, arch-agnostic files for %{name}.


%package %{pkgsimple %{clufter_lib}-general}
Group:          System Environment/Libraries
Summary:        Extra %{name} plugins usable for/as generic/auxiliary products
Requires:       %{clufter_lib} = %{version}-%{release}
BuildArch:      noarch

%description %{pkgsimple %{clufter_lib}-general}
This package contains set of additional plugins targeting variety of generic
formats often serving as a byproducts in the intermediate steps of the overall
process arrangement: either experimental commands or internally unused,
reusable formats and filters.


%package %{pkgsimple %{clufter_lib}-ccs}
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing CMAN configuration
Requires:       %{clufter_lib}-general = %{version}-%{release}
BuildArch:      noarch

%description %{pkgsimple %{clufter_lib}-ccs}
This package contains set of additional plugins targeting CMAN cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.


%package %{pkgsimple %{clufter_lib}-pcs}
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing Pacemaker configuration
Requires:       %{clufter_lib}-general = %{version}-%{release}
BuildArch:      noarch

%description %{pkgsimple %{clufter_lib}-pcs}
This package contains set of additional plugins targeting Pacemaker cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.


%prep
%if "%{clufter_version}" == "%{clufter_version_norm}"
%if 0%{?clufter_check} == 2
%autosetup -p1 -S git -b 1
%if "%{testver}" != "%{version}"
    %{__cp} -a ../"%{name}-%{testver}"/* .
%endif
%else
%autosetup -p1 -S git
%endif
%else
%autosetup -n %{clufter_source} -p1 -S git
%endif

## for some esoteric reason, the line above has to be empty
%{clufter_dopython} setup.py saveopts -f setup.cfg pkg_prepare \
                             --ccs-flatten='%{clufter_ccs_flatten}' \
                             --editor='%{clufter_editor}' \
                             --extplugins-shared='%{clufter_extplugins_shared}' \
                             --ra-metadata-dir='%{clufter_ra_metadata_dir}' \
                             --ra-metadata-ext='%{clufter_ra_metadata_ext}' \
                             --shell-posix='%{clufter_shell_posix}' \
                             --shell-bashlike='%{clufter_shell_bashlike}'
%{clufter_dopython} setup.py saveopts -f setup.cfg pkg_prepare \
  --report-bugs='%{clufter_url_bugs}'

%build
%if 0%{?clufter_pylib2:1}
%if 0%{?py2_build:1}
%py2_build
%else
# make Python interpreter execution sane (via -Es flags)
%{__python2} setup.py saveopts -f setup.cfg build_scripts \
                      --executable='%{__python2} %{?py2_shbang_opts}%{!?py2_shbang_opts:-Es}'
%{__python2} setup.py build
%endif
%endif

%if 0%{?clufter_pylib3:1}
# see https://fedoraproject.org/wiki/Changes/python3_c.utf-8_locale;
# specifically:
#   File "setup.py", line 466, in _pkg_prepare_file
#     content = fr.read()
#   File "/usr/lib64/python3.5/encodings/ascii.py", line 26, in decode
#     return codecs.ascii_decode(input, self.errors)[0]
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 221: ordinal not in range(128)
export LC_ALL=C.UTF-8 LANG=C.UTF-8
%if 0%{?py3_build:1}
%py3_build
%else
# make Python interpreter execution sane (via -Es flags)
%{__python3} setup.py saveopts -f setup.cfg build_scripts \
                      --executable='%{__python3} %{?py3_shbang_opts}%{!?py3_shbang_opts:-Es}'
%{__python3} setup.py build
%endif
%endif

%if %{with bashcomp}
%{clufter_dopython} ./run-dev --skip-ext --completion-bash 2>/dev/null \
  | sed 's|run[-_]dev|%{name}|g' > .bashcomp
%endif
%if %{with manpage}
# generate man pages (proper commands and aliases from a sorted sequence)
%{__mkdir_p} -- .manpages/man%{clufter_manpagesec}
{ echo; ./run-dev -l | sed -n 's|^  \(\S\+\).*|\1|p' | sort; } > .subcmds
sed -e 's:\(.\+\):\\\&\\fIrun_dev-\1\\fR\\\|(%{clufter_manpagesec}), :' \
  -e '1s|\(.*\)|\[SEE ALSO\]\n|' \
  -e '$s|\(.*\)|\1\nand perhaps more|' \
  .subcmds > .see-also
help2man -N -h -H -i .see-also \
  -n "$(sed -n '2s|[^(]\+(\([^)]\+\))|\1|p' README)" ./run-dev \
  | sed 's|run\\\?[-_]dev|%{name}|g' \
  > ".manpages/man%{clufter_manpagesec}/%{name}.%{clufter_manpagesec}"
while read cmd; do
  [ -n "${cmd}" ] || continue
  echo -e "#\!/bin/sh\n{ [ \$# -ge 1 ] && [ \"\$1\" = \"--version\" ] \
  && ./run-dev \"\$@\" || ./run-dev \"${cmd}\" \"\$@\"; }" > ".tmp-${cmd}"
  chmod +x ".tmp-${cmd}"
  grep -v "^${cmd}\$" .subcmds \
    | grep -e '^$' -e "$(echo ${cmd} | cut -d- -f1)\(-\|\$\)" \
    | sed -e 's:\(.\+\):\\\&\\fIrun_dev-\1\\fR\\\|(%{clufter_manpagesec}), :' \
      -e '1s|\(.*\)|\[SEE ALSO\]\n\\\&\\fIrun_dev\\fR\\\|(1), \n|' \
      -e '$s|\(.*\)|\1\nand perhaps more|' > .see-also
  # XXX uses ";;&" bashism
  case "${cmd}" in
  ccs[2-]*)
    sed -i \
      '1s:\(.*\):\1\n\\\&\\fIcluster.conf\\fR\\\|(5), \\\&\\fIccs\\fR\\\|(7), :' \
    .see-also
    ;;&
  ccs2pcs*)
    sed -i \
      '1s:\(.*\):\1\n\\\&\\fI%{_defaultdocdir}/%{clufter_source}/rgmanager-pacemaker\\fR\\\|, :' \
    .see-also
    ;;&
  *[2-]pcscmd*)
    sed -i '1s:\(.*\):\1\n\\\&\\fIpcs\\fR\\\|(8), :' .see-also
    ;;&
  esac
  help2man -N -h -H -i .see-also -n "${cmd}" "./.tmp-${cmd}" \
    | sed 's|run\\\?[-_]dev|%{name}|g' \
  > ".manpages/man%{clufter_manpagesec}/%{name}-${cmd}.%{clufter_manpagesec}"
done < .subcmds
%endif
%if %{with generated_schemas}
OUTPUTDIR=.schemas POSTPROCESS="%{SOURCE2}" sh "%{SOURCE3}" --clobber
%endif

%install
%if 0%{?clufter_pylib2:1}
%if 0%{?py2_install:1}
%py2_install
%else
# '--root' implies setuptools involves distutils to do old-style install
%{__python2} setup.py install --skip-build --root '%{buildroot}'
%endif
%endif

%if 0%{?clufter_pylib3:1}
%if 0%{?py3_install:1}
# see build section
export LC_ALL=C.UTF-8 LANG=C.UTF-8
%py3_install
%else
# '--root' implies setuptools involves distutils to do old-style install
%{__python3} setup.py install --skip-build --root '%{buildroot}'
%endif
%endif

# following is needed due to umask 022 not taking effect(?) leading to 775
%{__chmod} -- g-w '%{buildroot}%{clufter_ccs_flatten}'
%if %{with script}
# fix excessive script interpreting "executable" quoting with old setuptools:
# https://github.com/pypa/setuptools/issues/188
# https://bugzilla.redhat.com/1353934
sed -i '1s|^\(#!\)"\(.*\)"$|\1\2|' '%{buildroot}%{_bindir}/%{name}'
# %%%%{_bindir}/%%%%{name} should have been created
test -f '%{buildroot}%{clufter_script}' \
  || %{__install} -D -pm 644 -- '%{buildroot}%{_bindir}/%{name}' \
                                '%{buildroot}%{clufter_script}'

# move data files from python-specific locations to a single common one
# and possibly symlink that back
%{__mkdir_p} -- '%{buildroot}%{_datarootdir}/%{name}/formats'
for format in cib corosync; do
  %{__cp} -a -t '%{buildroot}%{_datarootdir}/%{name}/formats' \
          -- "%{buildroot}%{clufter_sitelib}/formats/${format}"
%if 0%{?clufter_pylib2:1}
  %{__rm} -f -- "%{buildroot}%{python2_sitelib}/%{name}/formats/${format}"/*
  ln -s -t "%{buildroot}%{python2_sitelib}/%{name}/formats/${format}" \
     -- $(pushd "%{buildroot}%{_datarootdir}/%{name}/formats/${format}" >/dev/null; \
          ls -1A | sed "s:.*:%{_datarootdir}/%{name}/formats/${format}/\\0:")
%endif
%if 0%{?clufter_pylib3:1}
  %{__rm} -f -- "%{buildroot}%{python3_sitelib}/%{name}/formats/${format}"/*
  ln -s -t "%{buildroot}%{python3_sitelib}/%{name}/formats/${format}" \
     -- $(pushd "%{buildroot}%{_datarootdir}/%{name}/formats/${format}" >/dev/null; \
          ls -1A | sed "s:.*:%{_datarootdir}/%{name}/formats/${format}/\\0:")
%endif
done

# move ext-plugins from python-specific locations to a single common one
# incl. the different sorts of precompiled bytecodes
%{__mkdir_p} -- '%{buildroot}%{clufter_extplugins_shared}'
%if 0%{?clufter_pylib2:1}
mv -t '%{buildroot}%{clufter_extplugins_shared}' \
   -- '%{buildroot}%{python2_sitelib}/%{name}'/ext-plugins/*/
%endif
%if 0%{?clufter_pylib3:1}
%if 0%{?clufter_pylib2:1}
%{__cp} -af -t '%{buildroot}%{clufter_extplugins_shared}' \
        -- '%{buildroot}%{python3_sitelib}/%{name}'/ext-plugins/*
%{__rm} -rf -- '%{buildroot}%{python3_sitelib}/%{name}'/ext-plugins/*/
%else
mv -t '%{buildroot}%{clufter_extplugins_shared}' \
   -- '%{buildroot}%{python3_sitelib}/%{name}'/ext-plugins/*/
%endif
%endif

%if %{with bashcomp}
declare bashcompdir="$(pkg-config --variable=completionsdir bash-completion \
                       || echo '%{clufter_bashcompdir}')"
declare bashcomp="${bashcompdir}/%{name}"
%if %{with bashcomplink}
%{__install} -D -pm 644 -- \
  .bashcomp '%{buildroot}%{clufter_bashcompreal}'
%{__mkdir_p} -- "%{buildroot}${bashcompdir}"
ln -s '%{clufter_bashcompreal}' "%{buildroot}${bashcomp}"
%else
%{__install} -D -pm 644 -- .bashcomp "%{buildroot}${bashcomp}"
%endif
# own %%%%{_datadir}/bash-completion in case of ...bash-completion/completions,
# more generally any path up to any of /, /usr, /usr/share, /etc
while true; do
  test "$(dirname "${bashcompdir}")" != "/" \
  && test "$(dirname "${bashcompdir}")" != "%{_prefix}" \
  && test "$(dirname "${bashcompdir}")" != "%{_datadir}" \
  && test "$(dirname "${bashcompdir}")" != "%{_sysconfdir}" \
  || break
  bashcompdir="$(dirname "${bashcompdir}")"
done
cat >.bashcomp-files <<-EOF
	${bashcompdir}
%if %{with bashcomplink}
	%%dir %(dirname '%{clufter_bashcompreal}')
	%%verify(not size md5 mtime) %{clufter_bashcompreal}
%else
	%%verify(not size md5 mtime) ${bashcomp}
%endif
EOF
%endif
%if %{with manpage}
%{__mkdir_p} -- '%{buildroot}%{_mandir}'
%{__cp} -a -t '%{buildroot}%{_mandir}' -- .manpages/*
%endif
%if %{with generated_schemas}
%{__cp} -a -f -t '%{buildroot}%{_datarootdir}/%{name}/formats/cib' \
              -- .schemas/pacemaker-*.*.rng
%endif
%endif
%{__mkdir_p} -- '%{buildroot}%{_defaultdocdir}/%{clufter_source}'
%{__cp} -a -t '%{buildroot}%{_defaultdocdir}/%{clufter_source}' \
           -- gpl-2.0.txt doc/*.txt doc/rgmanager-pacemaker

%check
%if 0%{clufter_check}
# just a basic sanity check
# we need to massage RA metadata files and PATH so the local run works
# XXX we could also inject buildroot's site_packages dir to PYTHONPATH
declare ret=0 \
        ccs_flatten_dir="$(dirname '%{buildroot}%{clufter_ccs_flatten}')"
ln -s '%{buildroot}%{clufter_ra_metadata_dir}'/*.'%{clufter_ra_metadata_ext}' \
      "${ccs_flatten_dir}"
%if %{clufter_check} == 1
%if 0%{?clufter_pylib2:1}
PATH="${PATH:+${PATH}:}${ccs_flatten_dir}" PYTHONEXEC="%{__python2} -Es" ./run-check
%endif
%if 0%{?clufter_pylib3:1}
# see build section
export LC_ALL=C.UTF-8 LANG=C.UTF-8
PATH="${PATH:+${PATH}:}${ccs_flatten_dir}" PYTHONEXEC="%{__python3} -Es" ./run-check
%endif
%else
%if 0%{?clufter_pylib2:1}
PATH="${PATH:+${PATH}:}${ccs_flatten_dir}" PYTHONEXEC="%{__python2} -Es" ./run-tests
%endif
%if 0%{?clufter_pylib3:1}
# see build section
export LC_ALL=C.UTF-8 LANG=C.UTF-8
PATH="${PATH:+${PATH}:}${ccs_flatten_dir}" PYTHONEXEC="%{__python3} -Es" ./run-tests
%endif
%endif
ret=$?
%{__rm} -f -- "${ccs_flatten_dir}"/*.'%{clufter_ra_metadata_ext}'
[ ${ret} -eq 0 ] || exit ${ret}
%endif

%if %{with bashcomp}
%post %{pkgsimple %{clufter_cli}}
if [ $1 -gt 1 ]; then  # no gain regenerating it w/ fresh install (same result)
declare bashcomp="%{?clufter_bashcompreal}%{!?clufter_bashcompreal:$(
    pkg-config --variable=completionsdir bash-completion 2>/dev/null \
    || echo '%{clufter_bashcompdir}')/%{name}}"
%{clufter_script} --completion-bash > "${bashcomp}" 2>/dev/null || :
fi
%endif


%global clufter_post_ext %(
cat <<EOF
declare bashcomp="%{?clufter_bashcompreal}%{!?clufter_bashcompreal:\\$(
    pkg-config --variable=completionsdir bash-completion 2>/dev/null \\\\
    || echo '%{clufter_bashcompdir}')/%{name}}"
# if the completion file is not present, suppose it is not desired
test -x '%{clufter_script}' && test -f "\\${bashcomp}" \\\\
  && %{clufter_script} --completion-bash > "\\${bashcomp}" 2>/dev/null || :
EOF)

%post %{pkgsimple %{clufter_lib}-general}
%{clufter_post_ext}

%post %{pkgsimple %{clufter_lib}-ccs}
%{clufter_post_ext}

%post %{pkgsimple %{clufter_lib}-pcs}
%{clufter_post_ext}


%if %{with script}
%if %{with bashcomp}
%files %{pkgsimple %{clufter_cli}} -f .bashcomp-files
%else
%files %{pkgsimple %{clufter_cli}}
%endif
%if %{with manpage}
%{_mandir}/man%{clufter_manpagesec}/*.%{clufter_manpagesec}*
%endif
%{clufter_script}
%endif

%if 0%{?clufter_pylib2:1}
%files %{pkgsimple %{clufter_pylib2}}
%{python2_sitelib}/%{name}
%{python2_sitelib}/%{name}-*.egg-info
%endif

%if 0%{?clufter_pylib3:1}
%files %{pkgsimple %{clufter_pylib3}}
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}-*.egg-info
%endif

%files %{pkgsimple %{clufter_bin}}
# /usr/libexec/clufter/ccs_flatten -> /usr/libexec/clufter
# /usr/libexec/ccs_flatten         -> /usr/libexec/ccs_flatten
%(echo '%{clufter_ccs_flatten}' | sed 's|\(%{_libexecdir}/[^/]\+\).*|\1|')

%files %{pkgsimple %{clufter_common}}
%{clufter_ra_metadata_dir}
%{_datarootdir}/%{name}
# following few paths will get marked as doc automatically based on location
%dir %{_defaultdocdir}/%{clufter_source}
%{_defaultdocdir}/%{clufter_source}/*[^[:digit:]]
%license %{_defaultdocdir}/%{clufter_source}/*[[:digit:]].txt

%files %{pkgsimple %{clufter_lib}-general}
%{clufter_extplugins_shared}/lib-general

%files %{pkgsimple %{clufter_lib}-ccs}
%{clufter_extplugins_shared}/lib-ccs

%files %{pkgsimple %{clufter_lib}-pcs}
%{clufter_extplugins_shared}/lib-pcs


%define cl_entry() %(LC_ALL=C date -d %1 "+* %%a %%b %%d %%Y %(echo "%3") - %2"
                     echo "%*" | sed '1d;s|^\\s\\+\\(.*\\)|- \\1|')
%global cl_jp_r Jan Pokorný <jpokorny+rpm-clufter @at@ fedoraproject .dot. org>
%global cl_jp   %(echo -n '%{cl_jp_r}' | sed 's| @at@ |@|;s| \.dot\. |.|g')
%changelog
%{cl_entry 2018-03-15 0.77.2-0.1.a %{cl_jp}
  TBD}

%{cl_entry 2018-03-14 0.77.1-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2017-11-10 0.77.0-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2017-06-06 0.76.0-1 %{cl_jp}
  factor "borrow validation schemas from pacemaker" out to a separate script
  bump upstream package}

%{cl_entry 2017-05-26 0.75.0-1 %{cl_jp}
  move nano fallback editor dependency to \-cli package [PGissue#1]}
  bump upstream package}

%{cl_entry 2017-03-21 0.70.0-1 %{cl_jp}
  split \-bin and \-common packages, the former becoming the only arch-specific
  also move python-specific (entry points, main files) back from \-cli package
  also rename python-clufter to python2-clufter (former is a legacy alias)
  also leverage the above modularization to package python3-clufter in parallel
  bump upstream package (version rolling the above changes out)}

%{cl_entry 2017-01-18 0.59.8-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-12-12 0.59.7-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-10-20 0.59.6-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-08-08 0.59.5-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-08-02 0.59.4-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-07-29 0.59.3-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-07-28 0.59.2-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-07-26 0.59.1-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-07-22 0.59.0-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-07-15 0.58.0-1 %{cl_jp}
  fix Python interpreter propagated as enquoted string with old setuptools
  bump upstream package}

%{cl_entry 2016-07-01 0.57.0-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-06-22 0.56.3-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-03-18 0.56.2-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2016-02-09 0.56.1-1 %{cl_jp}
  add ability to borrow validation schemas from pacemaker installed along
  bump upstream package}

%{cl_entry 2016-02-01 0.56.0-1 %{cl_jp}
  move entry_points.txt to %{pkgsimple %{clufter_cli}} sub-package
  general spec file refresh (pagure.io as a default project base, etc.)
  bump upstream package}

%{cl_entry 2015-12-17 0.55.0-1 %{cl_jp}
  bump upstream package (intentionally noticeable)}

%{cl_entry 2015-10-08 0.50.5-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-09-09 0.50.4-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-09-02 0.50.3-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-08-11 0.50.2-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-07-14 0.50.1-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-07-02 0.50.0-1 %{cl_jp}
  bump upstream package (intentionally excessive)}

%{cl_entry 2015-06-19 0.12.0-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-05-29 0.11.2-1 %{cl_jp}
  move completion module to %{pkgsimple %{clufter_cli}} sub-package
  bump upstream package}

%{cl_entry 2015-05-19 0.11.1-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-04-15 0.11.0-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-04-08 0.10.4-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-03-20 0.10.3-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-03-16 0.10.2-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-03-04 0.10.1-1 %{cl_jp}
  bump upstream package}

%{cl_entry 2015-02-26 0.10.0-1 %{cl_jp}
  packaging enhancements (structure, redundancy, ownership, scriptlets, symlink)
  version bump so as not to collide with python-clufter co-packaged with pcs}

%{cl_entry 2015-01-20 0.3.5-1 %{cl_jp}
  packaging enhancements (pkg-config, license tag)}

%{cl_entry 2015-01-14 0.3.4-1 %{cl_jp}
  packaging enhancements (permissions, ownership)
  man page for CLI frontend now included}

%{cl_entry 2015-01-13 0.3.3-1 %{cl_jp}
  initial build}
