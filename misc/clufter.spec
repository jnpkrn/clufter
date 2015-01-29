# distill-spec-prefix: clufter
%{!?clufter_version: %global clufter_version  0.3.6a}
%{!?clufter_name:    %global clufter_name     clufter}

%{!?clufter_source:  %global clufter_source   %{name}-%{clufter_version}}
%{!?clufter_url_main:%global clufter_url_main https://github.com/jnpkrn/}
%{!?clufter_url_dist:%global clufter_url_dist https://people.redhat.com/jpokorny/pkgs/}

%{!?clufter_check:   %global clufter_check    1}
%{!?clufter_pylib:   %global clufter_pylib    python-%{name}}
%{!?clufter_extlib:  %global clufter_extlib   %{name}-lib}

%{!?clufter_ccs_flatten:     %global clufter_ccs_flatten     %{_libexecdir}/%{clufter_source}/ccs_flatten}
%{!?clufter_editor:          %global clufter_editor          %{_bindir}/nano}
%{!?clufter_ra_metadata_dir: %global clufter_ra_metadata_dir %{_datadir}/cluster}
%{!?clufter_ra_metadata_ext: %global clufter_ra_metadata_ext metadata}

%bcond_without script
%if %{with script}
  %bcond_without bashcomp
  %bcond_without manpage
%endif
%if %{with script}
  %{!?clufter_cli:     %global clufter_cli      %{name}-cli}
  %{!?clufter_script:  %global clufter_script   %{_bindir}/%{name}}
  %if %{with bashcomp}
    %{!?clufter_bashcompdir:%global clufter_bashcompdir %{_sysconfdir}/bash_completion.d}
  %endif
  %if %{with manpage}
    %{!?clufter_manpagesec: %global clufter_manpagesec  1}
  %endif
%endif

# derived
%global clufter_version_norm %(echo '%{clufter_version}' | tr '-' '_' \\
  | sed 's|\\([0-9]\\)a\\(_.*\\)\\?$|\\1|')
# http://fedoraproject.org/wiki/Packaging:NamingGuidelines#Pre-Release_packages
%global clufter_rel %(echo '%{clufter_version}' | tr '-' '_' \\
  | sed -n 's|.*[0-9]a\\(_.*\\)\\?$|0.1.a\\1|p;tq;Q1;:q;q' || echo 1)

Name:           %{clufter_name}
Version:        %{clufter_version_norm}
Release:        %{clufter_rel}%{?dist}
Group:          System Environment/Base
Summary:        Tool/library for transforming/analyzing cluster configuration formats
License:        GPLv2+
URL:            %{clufter_url_main}%{name}

# autosetup
BuildRequires:  git

# Python side (first for python2* macros)
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
%if "0%{clufter_check}"
BuildRequires:  python-lxml
%endif

Source0:        %{clufter_url_dist}%{name}/%{name}-%{version}.tar.gz


%global clufter_description %(cat <<EOF
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.
EOF)

%description
%{clufter_description}


%if %{with script}
%package -n %{clufter_cli}
Group:          System Environment/Base
Summary:        Tool for transforming/analyzing cluster configuration formats
%if %{with manpage}
BuildRequires:  help2man
%endif
Requires:       %{clufter_pylib} = %{version}-%{release}
Provides:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description -n %{clufter_cli}
%{clufter_description}

This package contains clufter command-line interface for the underlying
library (packaged as %{clufter_pylib}).
%endif


%package -n %{clufter_pylib}
Group:          System Environment/Libraries
Summary:        Library for transforming/analyzing cluster configuration formats
License:        GPLv2+ and GFDL
# ccs_flatten helper
# ~ libxml2-devel
BuildRequires:  pkgconfig(libxml-2.0)
#autodected# Requires:       libxml2
Requires:       python-lxml
# "extras"
Requires:       %{clufter_editor}
# this is _arch-specific_

%description -n %{clufter_pylib}
%{clufter_description}

This package contains clufter library including built-in plugins.


%package -n %{clufter_extlib}-general
Group:          System Environment/Libraries
Summary:        Extra %{name} plugins usable for/as generic/auxiliary products
Requires:       %{clufter_pylib} = %{version}-%{release}
BuildArch:      noarch

%description -n %{clufter_extlib}-general
This package contains set of additional plugins targeting variety of generic
formats often serving as a byproducts in the intermediate steps of the overall
process arrangement: either experimental commands or internally unused,
reusable formats and filters.


%package -n %{clufter_extlib}-ccs
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing CMAN configuration
Requires:       %{clufter_pylib} = %{version}-%{release}
Requires:       %{clufter_extlib}-general = %{version}-%{release}
BuildArch:      noarch

%description -n %{clufter_extlib}-ccs
This package contains set of additional plugins targeting CMAN cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.


%package -n %{clufter_extlib}-pcs
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing Pacemaker configuration
Requires:       %{clufter_pylib} = %{version}-%{release}
Requires:       %{clufter_extlib}-general = %{version}-%{release}
BuildArch:      noarch

%description -n %{clufter_extlib}-pcs
This package contains set of additional plugins targeting Pacemaker cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.


%prep
%autosetup -n %{name}-%{clufter_version} -p1 -S git

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
# %%{_bindir}/%%{name} should have been created
test -f '%{buildroot}%{clufter_script}' \
  || %{__install} -D -pm 644 -- '%{buildroot}%{_bindir}/%{name}' \
                                '%{buildroot}%{clufter_script}'
%if %{with bashcomp}
declare bashcomp='%{clufter_bashcompdir}/%{name}'
%{__install} -D -pm 644 -- .bashcomp "%{buildroot}${bashcomp}"
cat >.bashcomp-files <<-EOF
	%{clufter_bashcompdir}
	%%verify(not size md5 mtime) ${bashcomp}
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
declare ret=0 ccs_flatten_dir="$(dirname '%{buildroot}%{clufter_ccs_flatten}')"

ln -s '%{buildroot}%{clufter_ra_metadata_dir}'/*.'%{clufter_ra_metadata_ext}' \
      "${ccs_flatten_dir}"
PATH="${PATH:+${PATH}:}${ccs_flatten_dir}" ./run-check
ret=$?
%{__rm} -f -- "${ccs_flatten_dir}"/*.'%{clufter_ra_metadata_ext}'
[ ${ret} -eq 0 ] || exit "${ret}"
%endif

%if %{with bashcomp}
%post
if [ $1 -gt 1 ]; then  # no gain regenerating it w/ fresh install (same result)
%{clufter_script} --completion-bash > '%{clufter_bashcompdir}/%{name}' \
  2>/dev/null || :
fi
%endif


%if %{with script}
%if %{with bashcomp}
%files -n %{clufter_cli} -f .bashcomp-files
%else
%files -n %{clufter_cli}
%endif
%license %{_defaultdocdir}/%{clufter_source}/gpl-2.0.txt
%if %{with manpage}
%{_mandir}/man%{clufter_manpagesec}/*.%{clufter_manpagesec}*
%endif
%{clufter_script}
%{python2_sitelib}/%{name}/__main__.py*
%{python2_sitelib}/%{name}/main.py*
%endif

%files -n %{clufter_pylib}
%doc %{_defaultdocdir}/%{clufter_source}
%license %{_defaultdocdir}/%{clufter_source}/gpl-2.0.txt
%license %{_defaultdocdir}/%{clufter_source}/fdl-1.3.txt
%exclude %{python2_sitelib}/%{name}/__main__.py*
%exclude %{python2_sitelib}/%{name}/main.py*
%exclude %{python2_sitelib}/%{name}/ext-plugins/*
%{python2_sitelib}/%{name}
%{python2_sitelib}/%{name}-*.egg-info
# /usr/libexec/clufter/ccs_flatten -> /usr/libexec/clufter
# /usr/libexec/ccs_flatten         -> /usr/libexec/ccs_flatten
%(echo '%{clufter_ccs_flatten}' | sed 's|\(%{_libexecdir}/[^/]\+\).*|\1|')
%{clufter_ra_metadata_dir}

%files -n %{clufter_extlib}-general
%{python2_sitelib}/%{name}/ext-plugins/lib-general

%files -n %{clufter_extlib}-ccs
%{python2_sitelib}/%{name}/ext-plugins/lib-ccs

%files -n %{clufter_extlib}-pcs
%{python2_sitelib}/%{name}/ext-plugins/lib-pcs


%define cl_entry() %(LC_ALL=C date -d %1 "+* %%a %%b %%e %%Y %(echo "%3") - %2"
                     echo "%*" | sed '1d;s|^\\s\\+\\(.*\\)|- \\1|')
%global cl_jp_r Jan Pokorný <jpokorny+rpm-clufter @at@ fedoraproject .dot. org>
%global cl_jp   %(echo -n '%{cl_jp_r}' | sed 's| @at@ |@|;s| \.dot\. |.|g')
%changelog
%{cl_entry 2015-01-20 0.3.6-0.1.a %{cl_jp}
  TBD}

%{cl_entry 2015-01-20 0.3.5-1 %{cl_jp}
  packaging enhancements (pkg-config, license tag)}

%{cl_entry 2015-01-14 0.3.4-1 %{cl_jp}
  packaging enhancements (permissions, ownership)
  man page for CLI frontend now included}

%{cl_entry 2015-01-13 0.3.3-1 %{cl_jp}
  initial build}
