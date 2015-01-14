%{!?clufter_name:    %global clufter_name     clufter}
%{!?clufter_version: %global clufter_version  0.3.4a}
%{!?clufter_check:   %global clufter_check    1}

%{!?clufter_pylib:   %global clufter_pylib    python-%{clufter_name}}
%{!?clufter_cli:     %global clufter_cli      %{clufter_name}-cli}
%{!?clufter_extlib:  %global clufter_extlib   %{clufter_name}-lib}
%{!?clufter_source:  %global clufter_source   %{clufter_name}-%{clufter_version}}
%{!?clufter_script:  %global clufter_script   %{_bindir}/%{clufter_name}}
%{!?clufter_bashcomp:%global clufter_bashcomp %{_sysconfdir}/bash_completion.d/%(basename '%{clufter_script}')}
%{!?clufter_manpage: %global clufter_manpage  %{_mandir}/man1/%(basename '%{clufter_script}')}

%{!?clufter_ccs_flatten:     %global clufter_ccs_flatten     %{_libexecdir}/%{clufter_source}/ccs_flatten}
%{!?clufter_editor:          %global clufter_editor          %{_bindir}/nano}
%{!?clufter_ra_metadata_dir: %global clufter_ra_metadata_dir %{_datadir}/cluster}
%{!?clufter_ra_metadata_ext: %global clufter_ra_metadata_ext metadata}

%{!?clufter_url_main:%global clufter_url_main https://github.com/jnpkrn/}
%{!?clufter_url_dist:%global clufter_url_dist https://people.redhat.com/jpokorny/pkgs/}

# derived
%global clufter_version_norm %(echo '%{clufter_version}' | tr '-' '_' | sed 's|\\([0-9]\\)a\\(_.*\\)\\?$|\\1|')
# http://fedoraproject.org/wiki/Packaging%3aNamingGuidelines#Pre-Release_packages
%global clufter_rel %(echo '%{clufter_version}' | tr '-' '_' | sed -n 's|.*[0-9]a\\(_.*\\)\\?$|0.1.a\\1|p;tq;Q1;:q;q' || echo 1)

Name:           %{clufter_name}
Version:        %{clufter_version_norm}
Release:        %{clufter_rel}%{?dist}
Group:          System Environment/Base
Summary:        Tool/library for transforming/analyzing cluster configuration formats
License:        GPLv2+
URL:            %{clufter_url_main}%{clufter_name}

# autosetup
BuildRequires:  git

# Python side (first for python2* macros)
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
%if "%{clufter_check}"
BuildRequires:  python-lxml
%endif

Source0:        %{clufter_url_dist}%{clufter_name}/%{clufter_source}.tar.gz


%global clufter_description %(cat <<EOF
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.
EOF)

%description
%{clufter_description}


%package -n %{clufter_cli}
Group:          System Environment/Base
Summary:        Tool for transforming/analyzing cluster configuration formats
%if "x%{clufter_script}" == "x"
%else
%if "x%{clufter_manpage}" == "x"
%else
BuildRequires:  help2man
%endif
%endif
Requires:       %{clufter_pylib}%{?_isa} = %{version}-%{release}
Provides:       %{clufter_name}          = %{version}-%{release}
BuildArch:      noarch

%description -n %{clufter_cli}
%{clufter_description}

This package contains clufter command-line interface for the underlying
library (packaged as (%{clufter_pylib}).


%package -n %{clufter_pylib}
Group:          System Environment/Libraries
Summary:        Library for transforming/analyzing cluster configuration formats
# ccs_flatten helper
BuildRequires:  libxml2-devel
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
Summary:        Extra clufter plugins usable for/as generic/auxiliary products
Requires:       %{clufter_pylib}%{?_isa} = %{version}-%{release}
BuildArch:      noarch

%description -n %{clufter_extlib}-general
%{clufter_description}

This package contains set of additional plugins targeting variety of generic
formats often serving as a byproducts in the intermediate steps of the overall
process arrangement: either experimental commands or internally unused,
reusable formats and filters.


%package -n %{clufter_extlib}-ccs
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing CMAN configuration
Requires:       %{clufter_pylib}%{?_isa}  = %{version}-%{release}
Requires:       %{clufter_extlib}-general = %{version}-%{release}
BuildArch:      noarch

%description -n %{clufter_extlib}-ccs
%{clufter_description}

This package contains set of additional plugins targeting CMAN cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.


%package -n %{clufter_extlib}-pcs
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing Pacemaker configuration
Requires:       %{clufter_pylib}%{?_isa}  = %{version}-%{release}
Requires:       %{clufter_extlib}-general = %{version}-%{release}
BuildArch:      noarch

%description -n %{clufter_extlib}-pcs
%{clufter_description}

This package contains set of additional plugins targeting Pacemaker cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.


%prep
%autosetup -n %{name}-%{clufter_version} -p1 -S git

## for some esoteric reason, the line above has to be empty
%{__python2} setup.py saveopts -f setup.cfg pkg_prepare              \
                      --ccs-flatten='%{clufter_ccs_flatten}'         \
                      --editor='%{clufter_editor}'                   \
                      --ra-metadata-dir='%{clufter_ra_metadata_dir}' \
                      --ra-metadata-ext='%{clufter_ra_metadata_ext}'

%build
%{__python2} setup.py build
%if "x%{clufter_script}" == "x"
%else
%if "x%{clufter_bashcomp}" == "x"
%else
./run-dev --completion-bash 2>/dev/null \
  | sed 's|run[-_]dev|%(basename %{clufter_bashcomp})|g' > .bashcomp
%endif
%if "x%{clufter_manpage}" == "x"
%else
help2man -N -h -H -n "$(sed -n '2s|[^(]\+(\([^)]\+\))|\1|p' README)" ./run-dev \
  | sed 's|run[-_]dev|%(basename %{clufter_manpage})|g' | gzip > .manpage
%endif
%endif

%install
# '--root' implies setuptools involves distutils to do old-style install
%{__python2} setup.py install --skip-build --root '%{buildroot}'
# following is needed due to umask 022 not taking effect(?) leading to 775
%{__chmod} -- g-w '%{buildroot}%{clufter_ccs_flatten}'
%if "x%{clufter_script}" == "x"
%else
# %%{_bindir}/%%{clufter_name} should have been created
test -f '%{buildroot}%{clufter_script}' \
  || %{__install} -D -m 644 -- '%{buildroot}%{_bindir}/%{clufter_name}' \
                               '%{buildroot}%{clufter_script}'
%if "x%{clufter_bashcomp}" == "x"
%else
%{__install} -D -m 644 -- .bashcomp '%{buildroot}%{clufter_bashcomp}'
%endif
%if "x%{clufter_manpage}" == "x"
%else
%{__install} -D -m 644 -- .manpage '%{buildroot}%{clufter_manpage}.1.gz'
%endif
%endif
%{__mkdir_p} -- '%{buildroot}%{_defaultdocdir}/%{clufter_source}'
%{__install} -m 644 -- gpl-2.0.txt doc/*.txt \
                       '%{buildroot}%{_defaultdocdir}/%{clufter_source}'

%check || :
%if "%{clufter_check}"
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

%post
%if "x%{clufter_bashcomp}" == "x"
%else
%if "x%{clufter_script}" == "x"
if [ $1 -gt 1 ]; then  # no gain regenerating it w/ fresh install (same result)
  %{__python2} -m %{clufter_name}.__main__ --completion-bash 2>/dev/null \
    | sed 's|%(basename '%{__python2}') [-_]m ||g' > '%{clufter_bashcomp}' || :
fi
%else
%{clufter_script} --completion-bash > '%{clufter_bashcomp}' 2>/dev/null || :
%endif
%endif

%files -n %{clufter_cli}
%doc %{_defaultdocdir}/%{clufter_source}/gpl-2.0.txt
%if "x%{clufter_script}" == "x"
%else
%if "x%{clufter_bashcomp}" == "x"
%else
%verify(not size md5 mtime) %{clufter_bashcomp}
%endif
%if "x%{clufter_manpage}" == "x"
%else
%doc %{clufter_manpage}.1.gz
%endif
%{clufter_script}
%endif
%{python2_sitelib}/%{clufter_name}/__main__.py*
%{python2_sitelib}/%{clufter_name}/main.py*

%files -n %{clufter_pylib}
%doc %{_defaultdocdir}/%{clufter_source}
%exclude %{clufter_script}
%exclude %{python2_sitelib}/%{clufter_name}/__main__.py*
%exclude %{python2_sitelib}/%{clufter_name}/main.py*
%exclude %{python2_sitelib}/%{clufter_name}/ext-plugins/lib-general
%exclude %{python2_sitelib}/%{clufter_name}/ext-plugins/lib-ccs
%exclude %{python2_sitelib}/%{clufter_name}/ext-plugins/lib-pcs
%{python2_sitelib}/%{clufter_name}
%{python2_sitelib}/%{clufter_name}-*.egg-info
# /usr/libexec/clufter/ccs_flatten -> /usr/libexec/clufter
# /usr/libexec/ccs_flatten         -> /usr/libexec/ccs_flatten
%(echo '%{clufter_ccs_flatten}' | sed 's|\(%{_libexecdir}/[^/]\+\).*|\1|')
%{clufter_ra_metadata_dir}

%files -n %{clufter_extlib}-general
%doc %{_defaultdocdir}/%{clufter_source}/gpl-2.0.txt
%{python2_sitelib}/%{clufter_name}/ext-plugins/lib-general

%files -n %{clufter_extlib}-ccs
%doc %{_defaultdocdir}/%{clufter_source}/gpl-2.0.txt
%{python2_sitelib}/%{clufter_name}/ext-plugins/lib-ccs

%files -n %{clufter_extlib}-pcs
%doc %{_defaultdocdir}/%{clufter_source}/gpl-2.0.txt
%{python2_sitelib}/%{clufter_name}/ext-plugins/lib-pcs


%define cl_entry() %(LC_ALL=C date -d %1 "+* %%a %%b %%e %%Y %(echo "%3") - %2"
                     echo "%*" | sed '1d;s|^\\s\\+\\(.*\\)|- \\1|')
%global cl_jp_r Jan Pokorný <jpokorny+rpm-clufter @at@ fedoraproject .dot. org>
%global cl_jp   %(echo -n '%{cl_jp_r}' | sed 's| @at@ |@|;s| \.dot\. |.|g')
%changelog
%{cl_entry 2015-01-14 0.3.4-0.1.a %{cl_jp}
  }
%{cl_entry 2015-01-13 0.3.3-1 %{cl_jp}
  initial build}
