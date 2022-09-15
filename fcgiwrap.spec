%global commit 99c942c90063c73734e56bacaa65f947772d9186

Summary:	Simple FastCGI wrapper for CGI scripts
Name:		fcgiwrap
Version:	1.1.0
Release:	0.1
License:	MIT
URL:		https://github.com/gnosek/fcgiwrap
Source0:	https://github.com/gnosek/fcgiwrap/archive/%{commit}/%{name}-%{commit}.tar.gz
# Source0-md5:	b092e95b676e23407732b4a2fbf800ae
Source1:	%{name}@.service
Source2:	%{name}@.socket
Source3:	%{name}.sysconfig
# https://github.com/gnosek/fcgiwrap/pull/39
Patch0:		%{name}-1.1.0-use_pkg-config_libsystemd.patch
# https://github.com/gnosek/fcgiwrap/pull/43
Patch1:		%{name}-1.1.0-declare_cgi_error_noreturn.patch
# https://github.com/gnosek/fcgiwrap/pull/44
Patch2:		%{name}-1.1.0-fix_kill_param_sequence.patch
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	coreutils
BuildRequires:	fcgi-devel
BuildRequires:	gcc
BuildRequires:	systemd-devel

%description
This package provides a simple FastCGI wrapper for CGI scripts with/
following features:
 - very lightweight (84KB of private memory per instance)
 - fixes broken CR/LF in headers
 - handles environment in a sane way (CGI scripts get HTTP-related
   environment vars from FastCGI parameters and inherit all the others
   from environment of fcgiwrap )
 - no configuration, so you can run several sites off the same fcgiwrap
   pool
 - passes CGI std error output to std error stream of cgiwrap or
   FastCGI
 - support systemd socket activation, launcher program like spawn-fcgi
   is no longer required on systemd-enabled distributions

%prep
%setup -q -n %{name}-%{commit}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
autoreconf -i
%configure \
    CFLAGS="-I%{_includedir}/fastcgi %{rpmcflags}" \
    --prefix="" \
    --with-systemd

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# Remove the default systemd files
rm -f $RPM_BUILD_ROOT%{systemdunitdir}/fcgiwrap.service
rm -f $RPM_BUILD_ROOT%{systemdunitdir}/fcgiwrap.socket

# Install our own systemd config files
install -Dm 644 %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}@.service
install -Dm 644 %{SOURCE2} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}@.socket
install -Dm 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

%post
%systemd_post %{name}@.service %{name}@.socket

%preun
%systemd_preun %{name}@.service %{name}@.socket

%postun
%systemd_postun_with_restart %{name}@.service %{name}@.socket

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.rst COPYING
%attr(755,root,root) %{_sbindir}/%{name}
%{_mandir}/man8/%{name}.8*
%{systemdunitdir}/%{name}@.service
%{systemdunitdir}/%{name}@.socket
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
