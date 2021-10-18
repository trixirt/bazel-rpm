Name:           bazel
Summary:        A java based build system
Version:        3.7.2
Release:        5%{?dist}
License:        ASL 2.0
ExclusiveArch:  x86_64 aarch64
URL:            http://bazel.io/
Source0:        https://github.com/bazelbuild/bazel/releases/download/%{version}/bazel-%{version}-dist.zip

# Silince log.warning bactrace
# From the original bazel4 project
Patch1:         bazel-1.0.0-log-warning.patch
# Fixes up some include problems with the bootstapped bazel
# From the original bazel4 project
Patch2:         bazel-gcc.patch

BuildRequires:  bash-completion
BuildRequires:  findutils
BuildRequires:  gcc-c++
BuildRequires:  java-11-openjdk-devel
BuildRequires:  python3
BuildRequires:  python-unversioned-command
BuildRequires:  unzip
BuildRequires:  which
BuildRequires:  zip
BuildRequires:  zlib-devel

Requires:       bash
# bazel assumes you are building something
# If you only install java-11-openjdk you will see an error like
# FATAL: Could not find system javabase. Ensure JAVA_HOME is set, or javac is on your PATH.
Requires:       java-11-openjdk-devel

%description
A java based build system.

%package devel
Summary:        A java based build system

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
# The bazel args workaround depends on the major verion of gcc to find the c++/limits file
# Assume the first line looks like
# gcc (GCC) 11.2.1 20210728 (Red Hat 11.2.1-1)
%define gcc_major %(gcc --version | grep GCC | tr '.' ' ' | awk '{ print $3 }')

%description devel
A java based build system.

%prep
%setup -q -c -n bazel-%{version}
%patch1 -p0
%patch2 -p0
# Fix the license file being distributed with execute permissions.
chmod a-x LICENSE

%build
# Set the release date and version
export SOURCE_DATE_EPOCH="$(date -d $(head -1 CHANGELOG.md | %{__grep} -Eo '\b[[:digit:]]{4}-[[:digit:]]{2}-[[:digit:]]{2}\b' ) +%s)"
export EMBED_LABEL="%{version}"
# Recommended bootstrapping arg from
# https://docs.bazel.build/versions/3.7.0/install-compile-source.html
EXTRA_BAZEL_ARGS="--host_javabase=@local_jdk//:jdk"
# Work around some compile problems
export EXTRA_BAZEL_ARGS="$EXTRA_BAZEL_ARGS --cxxopt=-include/usr/include/c++/%{gcc_major}/limits"
# Use the real which
# In the mock build, there is this build error
# environment: line 1: which_declare: command not found
unset -f which
# bazel bootstraps then and builds itself again.
# Use the project's script instead of expanding the script here.
env ./compile.sh
# Generate the bash completions
env ./scripts/generate_bash_completion.sh --bazel=output/bazel --output=output/bazel-complete.bash

%install
# license
%{__mkdir_p} %{buildroot}%{_datadir}/bazel
%{__cp} LICENSE %{buildroot}%{_datadir}/bazel/LICENSE
# bash completion
%{__mkdir_p} %{buildroot}/%{bashcompdir}
%{__cp} output/bazel-complete.bash %{buildroot}/%{bashcompdir}/bazel
# bazel and wrapper
%{__mkdir_p} %{buildroot}/%{_bindir}
%{__cp} output/bazel %{buildroot}/%{_bindir}/bazel-%{bazel_version}
%{__cp} ./scripts/packages/bazel.sh %{buildroot}/%{_bindir}/bazel

%files devel
%dir %{_datadir}/bazel
%license %{_datadir}/bazel/LICENSE
%{_bindir}/bazel
%{_bindir}/bazel-%{bazel_version}
%{bashcompdir}/bazel

%changelog
* Mon Oct 18 2021 <trix@redhat.com> - 3.7.2-5
- Move requires list out of description

* Sun Oct 17 2021 <trix@redhat.com> - 3.7.2-4
- Remove 4.2.1 cruft
- Order build requires list alphabetically
- builds on aarch64

* Sat Oct 16 2021 <trix@redhat.com> - 3.7.2-3
- Define/use gcc_major in bazel args
- For mock, use local jdk instead of trying to download one
- For mock, require python-unversioned-command because some use of 'python'
- Remove debugging cruft
- java devel is required, bazel devel is required

* Thu Oct 14 2021 <trix@redhat.com> - 3.7.2-2
- Restore bazel4 requires on java-11-openjdk-devel

* Wed Oct 13 2021 <trix@redhat.com> - 3.7.2-1
- Change to 3.7.2 for building tensorflow
- Change bazel-real to bazel-<version>-<os_arch_suffix>

* Sun Oct 10 2021 <trix@redhat.com> - 4.2.1-1
- Initial version
- Forked from http://copr-dist-git.fedorainfracloud.org/git/vbatts/bazel/bazel4.git


