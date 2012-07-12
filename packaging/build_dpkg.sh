set -x
VERSION="1.0.0"
rm -rf pkg/*
rm -rf debian/
# make necessary directories
mkdir pkg
mkdir debian
mkdir debian/DEBIAN
mkdir debian/usr/
mkdir debian/usr/share
mkdir debian/usr/share/ptracetools
mkdir debian/usr/local/
mkdir debian/usr/local/bin/
mkdir debian/usr/local/lib/
mkdir debian/usr/share/applications
# copy files over
cp ../ptrace-gui/*.py debian/usr/share/ptracetools/
cp ../ptrace-analyze/*.py debian/usr/local/bin/
cp ../ptrace-tool/pthread-trace debian/usr/local/bin/
cp ../ptrace-tool/libpthread-trace.so debian/usr/local/lib/
cp ptrace.png debian/usr/share/ptracetools/ptrace.png
cp control debian/DEBIAN/
cp postinst debian/DEBIAN/
cp postrm debian/DEBIAN/
cp ptrace-tools.desktop debian/usr/share/applications/
#build package
dpkg-deb --build debian
mv debian.deb pkg/ptrace-tools-$VERSION.deb

