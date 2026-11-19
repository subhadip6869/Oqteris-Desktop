Name:           oqteris
Version:        1.2.0
Release:        1
Summary:        Complete Cross-Platform PDF Reader and Editor
License:        Apache-2.0
URL:            https://originsd.vercel.app
AutoReqProv:    no

%define _build_id_links none
%define debug_package %{nil}
%define __strip /bin/true

%description
Oqteris is a dedicated desktop PDF reader, editor, annotator, and security
suite built with Python and Qt Quick/QML. Features high-performance rendering,
digital signatures validation, OCR recognition, and document optimization.

%install
mkdir -p %{buildroot}/opt/oqteris
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps

# Copy standalone binaries to /opt/oqteris
cp -r %{_sourcedir}/dist/Oqteris.dist/* %{buildroot}/opt/oqteris/
chmod +x %{buildroot}/opt/oqteris/Oqteris*

# Launcher script in /usr/bin/oqteris
cat << 'EOF' > %{buildroot}/usr/bin/oqteris
#!/bin/sh
exec /opt/oqteris/Oqteris "$@"
EOF
chmod +x %{buildroot}/usr/bin/oqteris

# Desktop integration
cp %{_sourcedir}/packaging/linux/app.vercel.originsd.oqteris.desktop %{buildroot}/usr/share/applications/
cp %{_sourcedir}/assets/icons/app/oqteris-logo.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/app.vercel.originsd.oqteris.png

%files
/opt/oqteris
/usr/bin/oqteris
/usr/share/applications/app.vercel.originsd.oqteris.desktop
/usr/share/icons/hicolor/256x256/apps/app.vercel.originsd.oqteris.png
