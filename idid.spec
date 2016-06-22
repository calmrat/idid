Name: idid
Version: 0.1
Release: 1%{?dist}

Summary: Save and share your daily activities!
License: GPLv2

URL: https://github.com/kejbaly2/idid
Source: https://github.com/kejbaly2/idid/releases/download/%{version}/idid-%{version}.tar.bz2

BuildArch: noarch
BuildRequires: python-devel
Requires: python-dateutil
%{?el6:Requires: python-argparse}

%description
Comfortably save and recall details of what you accomplished in a 
given day, week, month, quarter, year or selected date range.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{python_sitelib}/idid
install -pm 755 bin/idid %{buildroot}%{_bindir}/idid
install -pm 644 idid/*.py %{buildroot}%{python_sitelib}/idid
install -pm 644 idid.1.gz %{buildroot}%{_mandir}/man1


%files
%{_mandir}/man1/*
%{_bindir}/idid
%{python_sitelib}/*
%doc README.rst examples
%{!?_licensedir:%global license %%doc}
%license LICENSE

%changelog
* Fri Jun 17 2016 Chris Ward <kejbaly2@gmail.com> 0.1-1
- Forked from github.com/psss/did as separate app
