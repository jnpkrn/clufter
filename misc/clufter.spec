# distill-spec-prefix: clufter
%{!?clufter_version: %global clufter_version  %{?!infer:0.10.2}%{?infer:%(
                                                python ../setup.py --version)}}
%{!?clufter_name:    %global clufter_name     %{?!infer:clufter}%{?infer:%(
                                                python ../setup.py --name)}}
%{!?clufter_license: %global clufter_license  %{?!infer:GPLv2+}%{?infer:%(
                                                python ../setup.py --license)}}
%{!?clufter_check:   %global clufter_check    1}

# special vars wrt. versioning
%{!?clufter_b:       %global clufter_b        1}
%global clufter_version_norm %(echo '%{clufter_version}' | tr '-' '_' \\
  | sed 's|\\([0-9]\\)a\\(_.*\\)\\?$|\\1|')
# http://fedoraproject.org/wiki/Packaging:NamingGuidelines#Pre-Release_packages
%global clufter_githash %(echo '%{clufter_version}' | tr '-' '_' \\
  | sed -n 's|.*[0-9]a_git\\.\\(.*\\)|\\1|p')
%global clufter_rel %(echo '%{clufter_githash}' \\
  | sed -n 'bS;:E;n;:S;s|\\(.\\+\\)|0.%{clufter_b}.a_\\1|p;tE;c\\%{clufter_b}')

%if "%{clufter_version}" == "%{clufter_version_norm}"
%{!?clufter_source:  %global clufter_source   %{name}-%{version}}
%else
%{!?clufter_source:  %global clufter_source   %{name}-%{clufter_version}}
%endif
%{!?clufter_url_main:%global clufter_url_main https://github.com/jnpkrn/}
%{!?clufter_url_raw: %global clufter_url_raw  https://raw.githubusercontent.com/jnpkrn/}
%{!?clufter_url_dist:%global clufter_url_dist https://people.redhat.com/jpokorny/pkgs/}

%{!?clufter_pylib:   %global clufter_pylib    python-%{name}}
%{!?clufter_extlib:  %global clufter_extlib   %{name}-lib}

# Python package customizations
%{!?clufter_ccs_flatten:     %global clufter_ccs_flatten     %{_libexecdir}/%{clufter_source}/ccs_flatten}
%{!?clufter_editor:          %global clufter_editor          %{_bindir}/nano}
%{!?clufter_ra_metadata_dir: %global clufter_ra_metadata_dir %{_datadir}/cluster}
%{!?clufter_ra_metadata_ext: %global clufter_ra_metadata_ext metadata}

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


Name:           %{clufter_name}
Version:        %{clufter_version_norm}
Release:        %{clufter_rel}%{?dist}
Group:          System Environment/Base
Summary:        Tool/library for transforming/analyzing cluster configuration formats
License:        %{clufter_license}
URL:            %{clufter_url_main}%{name}

# autosetup
BuildRequires:  git

# Python side (first for python2* macros)
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
%if "0%{clufter_check}"
BuildRequires:  python-lxml
%endif

%if "%{clufter_version}" == "%{clufter_version_norm}"
Source0:        %{clufter_url_dist}%{name}/%{name}-%{version}.tar.gz
%else
Source0:        %{clufter_source}.tar.gz
# Source0 is created by Source1, just pass particular commit hash
# via GITHASH env. variable
Source1:        %{clufter_url_raw}%{name}/%{clufter_githash}/misc/run-sdist-per-commit
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
%if %{with bashcomp}
# for pkg-config file to be inspected during install phase
BuildRequires:  bash-completion
%endif
%if %{with manpage}
BuildRequires:  help2man
%endif
Requires:       %{clufter_pylib} = %{version}-%{release}
Provides:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description %{pkgsimple %{clufter_cli}}
%{clufter_description}

This package contains %{name} command-line interface for the underlying
library (packaged as %{clufter_pylib}).
%endif


%package %{pkgsimple %{clufter_pylib}}
Group:          System Environment/Libraries
Summary:        Library for transforming/analyzing cluster configuration formats
License:        %{clufter_license} and GFDL
# ccs_flatten helper
# ~ libxml2-devel
BuildRequires:  pkgconfig(libxml-2.0)
#autodected# Requires:       libxml2
Requires:       python-lxml
# "extras"
Requires:       %{clufter_editor}
# this is _arch-specific_

%description %{pkgsimple %{clufter_pylib}}
%{clufter_description}

This package contains %{name} library including built-in plugins.


%package %{pkgsimple %{clufter_extlib}-general}
Group:          System Environment/Libraries
Summary:        Extra %{name} plugins usable for/as generic/auxiliary products
Requires:       %{clufter_pylib} = %{version}-%{release}
BuildArch:      noarch

%description %{pkgsimple %{clufter_extlib}-general}
This package contains set of additional plugins targeting variety of generic
formats often serving as a byproducts in the intermediate steps of the overall
process arrangement: either experimental commands or internally unused,
reusable formats and filters.


%package %{pkgsimple %{clufter_extlib}-ccs}
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing CMAN configuration
Requires:       %{clufter_pylib} = %{version}-%{release}
Requires:       %{clufter_extlib}-general = %{version}-%{release}
BuildArch:      noarch

%description %{pkgsimple %{clufter_extlib}-ccs}
This package contains set of additional plugins targeting CMAN cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.


%package %{pkgsimple %{clufter_extlib}-pcs}
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing Pacemaker configuration
Requires:       %{clufter_pylib} = %{version}-%{release}
Requires:       %{clufter_extlib}-general = %{version}-%{release}
BuildArch:      noarch

%description %{pkgsimple %{clufter_extlib}-pcs}
This package contains set of additional plugins targeting Pacemaker cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.


%prep
%if "%{clufter_version}" == "%{clufter_version_norm}"
%autosetup -p1 -S git
%else
%autosetup -n %{clufter_source} -p1 -S git
%endif

## for some esoteric reason, the line above has to be empty
%{__python2} setup.py saveopts -f setup.cfg pkg_prepare \
                      --ccs-flatten='%{clufter_ccs_flatten}' \
                      --editor='%{clufter_editor}' \
                      --ra-metadata-dir='%{clufter_ra_metadata_dir}' \
                      --ra-metadata-ext='%{clufter_ra_metadata_ext}'

%build
%{__python2} setup.py build
%if %{with bashcomp}
./run-dev --skip-ext --completion-bash 2>/dev/null \
  | sed 's|run[-_]dev|%{name}|g' > .bashcomp
%endif
%if %{with manpage}
%{__mkdir_p} -- .manpages/man%{clufter_manpagesec}
help2man -N -h -H -n "$(sed -n '2s|[^(]\+(\([^)]\+\))|\1|p' README)" ./run-dev \
  | sed 's|run[-_]dev|%{name}|g' \
  > .manpages/man%{clufter_manpagesec}/%{name}.%{clufter_manpagesec}
%endif

%install
# '--root' implies setuptools involves distutils to do old-style install
%{__python2} setup.py install --skip-build --root '%{buildroot}'
# following is needed due to umask 022 not taking effect(?) leading to 775
%{__chmod} -- g-w '%{buildroot}%{clufter_ccs_flatten}'
%if %{with script}
# %%%%{_bindir}/%%%%{name} should have been created
test -f '%{buildroot}%{clufter_script}' \
  || %{__install} -D -pm 644 -- '%{buildroot}%{_bindir}/%{name}' \
                                '%{buildroot}%{clufter_script}'
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
%{__cp} -a -- .manpages/* '%{buildroot}%{_mandir}'
%endif
%endif
%{__mkdir_p} -- '%{buildroot}%{_defaultdocdir}/%{clufter_source}'
%{__install} -pm 644 -- gpl-2.0.txt doc/*.txt \
                        '%{buildroot}%{_defaultdocdir}/%{clufter_source}'

%check
%if "0%{clufter_check}"
# just a basic sanity check
# we need to massage RA metadata files and PATH so the local run works
# XXX we could also inject buildroot's site_packages dir to PYTHONPATH
declare ret=0 \
        ccs_flatten_dir="$(dirname '%{buildroot}%{clufter_ccs_flatten}')"
ln -s '%{buildroot}%{clufter_ra_metadata_dir}'/*.'%{clufter_ra_metadata_ext}' \
      "${ccs_flatten_dir}"
PATH="${PATH:+${PATH}:}${ccs_flatten_dir}" ./run-check
ret=$?
%{__rm} -f -- "${ccs_flatten_dir}"/*.'%{clufter_ra_metadata_ext}'
[ ${ret} -eq 0 ] || exit ${ret}
%endif

%if %{with bashcomp}
%post %{pkgsimple %{clufter_cli}}
if [ $1 -gt 1 ]; then  # no gain regenerating it w/ fresh install (same result)
declare bashcomp="%{?clufter_bashcompreal}%{?!clufter_bashcompreal:$(
    pkg-config --variable=completionsdir bash-completion 2>/dev/null \
    || echo '%{clufter_bashcompdir}')/%{name}}"
%{clufter_script} --completion-bash > "${bashcomp}" 2>/dev/null || :
fi
%endif


%global clufter_post_ext %(
cat <<EOF
declare bashcomp="%{?clufter_bashcompreal}%{?!clufter_bashcompreal:\\$(
    pkg-config --variable=completionsdir bash-completion 2>/dev/null \\\\
    || echo '%{clufter_bashcompdir}')/%{name}}"
# if the completion file is not present, suppose it is not desired
test -x '%{clufter_script}' && test -f "\\${bashcomp}" \\\\
  && %{clufter_script} --completion-bash > "\\${bashcomp}" 2>/dev/null || :
EOF)

%post %{pkgsimple %{clufter_extlib}-general}
%{clufter_post_ext}

%post %{pkgsimple %{clufter_extlib}-ccs}
%{clufter_post_ext}

%post %{pkgsimple %{clufter_extlib}-pcs}
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
%{python2_sitelib}/%{name}/__main__.py*
%{python2_sitelib}/%{name}/main.py*
%endif

%files %{pkgsimple %{clufter_pylib}}
# following few paths will get marked as doc automatically based on location
%dir %{_defaultdocdir}/%{clufter_source}
%{_defaultdocdir}/%{clufter_source}/*[^[:digit:]].txt
%license %{_defaultdocdir}/%{clufter_source}/*[[:digit:]].txt
%exclude %{python2_sitelib}/%{name}/__main__.py*
%exclude %{python2_sitelib}/%{name}/main.py*
%exclude %{python2_sitelib}/%{name}/ext-plugins/*/
%{python2_sitelib}/%{name}
%{python2_sitelib}/%{name}-*.egg-info
# /usr/libexec/clufter/ccs_flatten -> /usr/libexec/clufter
# /usr/libexec/ccs_flatten         -> /usr/libexec/ccs_flatten
%(echo '%{clufter_ccs_flatten}' | sed 's|\(%{_libexecdir}/[^/]\+\).*|\1|')
%{clufter_ra_metadata_dir}

%files %{pkgsimple %{clufter_extlib}-general}
%{python2_sitelib}/%{name}/ext-plugins/lib-general

%files %{pkgsimple %{clufter_extlib}-ccs}
%{python2_sitelib}/%{name}/ext-plugins/lib-ccs

%files %{pkgsimple %{clufter_extlib}-pcs}
%{python2_sitelib}/%{name}/ext-plugins/lib-pcs


%define cl_entry() %(LC_ALL=C date -d %1 "+* %%a %%b %%e %%Y %(echo "%3") - %2"
                     echo "%*" | sed '1d;s|^\\s\\+\\(.*\\)|- \\1|')
%global cl_jp_r Jan Pokorný <jpokorny+rpm-clufter @at@ fedoraproject .dot. org>
%global cl_jp   %(echo -n '%{cl_jp_r}' | sed 's| @at@ |@|;s| \.dot\. |.|g')
%changelog
%{cl_entry 2015-02-26 0.10.2-0.1.a %{cl_jp}
  TBD}

%{cl_entry 2015-03-04 0.10.1-1 %{cl_jp}
  bump upstream package
}
%{cl_entry 2015-02-26 0.10.0-1 %{cl_jp}
  packaging enhacements (structure, redundancy, ownership, scriptlets, symlink)
  version bump so as not to collide with python-clufter co-packaged with pcs}

%{cl_entry 2015-01-20 0.3.5-1 %{cl_jp}
  packaging enhancements (pkg-config, license tag)}

%{cl_entry 2015-01-14 0.3.4-1 %{cl_jp}
  packaging enhancements (permissions, ownership)
  man page for CLI frontend now included}

%{cl_entry 2015-01-13 0.3.3-1 %{cl_jp}
  initial build}
