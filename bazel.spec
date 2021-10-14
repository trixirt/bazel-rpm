Name:           bazel
Version:        3.7.2
Release:        2%{?dist}
Summary:        A java based build system
License:        ASL 2.0
ExclusiveArch:  x86_64

URL:            http://bazel.io/
Source0:        https://github.com/bazelbuild/bazel/releases/download/%{version}/bazel-%{version}-dist.zip

# Silince log.warning bactrace
# From the original baze4 project
Patch1:         bazel-1.0.0-log-warning.patch
# Fixes up some include problems with the bootstapped bazel
# From the original baze4 project
Patch2:         bazel-gcc.patch
# For man pages
# From https://github.com/bazelbuild/bazel/pull/12028/commits
# Fuzzing of 0 makes it difficult to use.
# This patch is for 4.2.1
Patch3:         bazel-manpage.patch

BuildRequires:  bash-completion
BuildRequires:  java-11-openjdk-devel
BuildRequires:  zlib-devel
BuildRequires:  findutils
BuildRequires:  gcc-c++
BuildRequires:  which
BuildRequires:  unzip
BuildRequires:  zip
BuildRequires:  python3

Requires:       bash
# bazel assumes you are building something
# If you only install java-11-openjdk you will see an error like
# FATAL: Could not find system javabase. Ensure JAVA_HOME is set, or javac is on your PATH.
Requires:       java-11-openjdk-devel

# where to install the bazel-complete.bash file
%define bashcompdir %(pkg-config --variable=completionsdir bash-completion 2>/dev/null)
# No debug package
%global debug_package %{nil}
# Normally stripping is fine, however the bazel exe
# is a wrapper around a zip archive and stripping it destoys the archive
# See issue here  https://github.com/vbatts/copr-build-bazel/issues/4
# Stripping exe's is one of several things done in os post install
# Since there is only 1 exe, just disable brp-strip
%define __brp_strip %{nil}
# The bazel wrapper has a fine grained version handling bazel-<version>-<os_arch_suffix>
%define bazel_version %{version}-linux-%{_arch}

%description
A java based build system.

%prep
%setup -q -c -n bazel-%{version}
%patch1 -p0
%patch2 -p0
%if "%{version}" == "4.2.1"
%patch3 -p1
%endif
# Fix the license file being distributed with execute permissions.
chmod a-x LICENSE

%build
# Set the release date and version
export SOURCE_DATE_EPOCH="$(date -d $(head -1 CHANGELOG.md | %{__grep} -Eo '\b[[:digit:]]{4}-[[:digit:]]{2}-[[:digit:]]{2}\b' ) +%s)"
export EMBED_LABEL="%{version}"
# Uncomment for debugging
# export CXXFLAGS="-g -O0"
# Work around some compile problems
export EXTRA_BAZEL_ARGS="--cxxopt=-include/usr/include/c++/11/limits"
# bazel bootstraps then and builds itself again.
# Use the project's script instead of expanding the script here.
env ./compile.sh
# Generate the bash completions
env ./scripts/generate_bash_completion.sh --bazel=output/bazel --output=output/bazel-complete.bash

%install
# license
%{__mkdir_p} %{buildroot}%{_datadir}/bazel
%{__cp} LICENSE %{buildroot}%{_datadir}/bazel/LICENSE
%if "%{version}" == "4.2.1"
# man page
%{__mkdir_p} %{buildroot}%{_mandir}/man1
%{__cp} bazel.1 %{buildroot}%{_mandir}/man1/
%endif
# bash completion
%{__mkdir_p} %{buildroot}/%{bashcompdir}
%{__cp} output/bazel-complete.bash %{buildroot}/%{bashcompdir}/bazel
# bazel and wrapper
%{__mkdir_p} %{buildroot}/%{_bindir}
%{__cp} output/bazel %{buildroot}/%{_bindir}/bazel-%{bazel_version}
%{__cp} ./scripts/packages/bazel.sh %{buildroot}/%{_bindir}/bazel

%files
%dir %{_datadir}/bazel
%license %{_datadir}/bazel/LICENSE
%if "%{version}" == "4.2.1"
%{_mandir}/man1/bazel.1.gz
%endif
%{_bindir}/bazel
%{_bindir}/bazel-%{bazel_version}
%{bashcompdir}/bazel

# Uncomment if you want to see the buildroot
# ex/ to verify that bazel-real was not strippped
# %clean
# echo "no cleaning for you"

%changelog
* Thu Oct 14 2021 <trix@redhat.com> - 3.7.2-2
- Restore bazel4 requires on java-11-openjdk-devel

* Wed Oct 13 2021 <trix@redhat.com> - 3.7.2-1
- Change to 3.7.2 for building tensorflow
- Change bazel-real to bazel-<version>-<os_arch_suffix>

* Sun Oct 10 2021 <trix@redhat.com> - 4.2.1-1
- Initial version
- Forked from http://copr-dist-git.fedorainfracloud.org/git/vbatts/bazel/bazel4.git


