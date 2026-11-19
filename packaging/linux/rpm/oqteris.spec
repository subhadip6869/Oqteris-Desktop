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
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/mimetypes

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
cp %{_sourcedir}/assets/icons/app/oqteris-logo.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/oqteris.png

# Document thumbnail icons for PDF mime types
cp %{_sourcedir}/assets/icons/document/oqteris-document.png %{buildroot}/usr/share/icons/hicolor/256x256/mimetypes/application-pdf.png
cp %{_sourcedir}/assets/icons/document/oqteris-document.png %{buildroot}/usr/share/icons/hicolor/256x256/mimetypes/application-x-pdf.png
cp %{_sourcedir}/assets/icons/document/oqteris-document.png %{buildroot}/usr/share/icons/hicolor/256x256/mimetypes/gnome-mime-application-pdf.png

%post
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q /usr/share/applications &> /dev/null || :
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor &> /dev/null || :
fi

%postun
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q /usr/share/applications &> /dev/null || :
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor &> /dev/null || :
fi

%files
/opt/oqteris
/usr/bin/oqteris
/usr/share/applications/app.vercel.originsd.oqteris.desktop
/usr/share/icons/hicolor/256x256/apps/app.vercel.originsd.oqteris.png
/usr/share/icons/hicolor/256x256/apps/oqteris.png
/usr/share/icons/hicolor/256x256/mimetypes/application-pdf.png
/usr/share/icons/hicolor/256x256/mimetypes/application-x-pdf.png
/usr/share/icons/hicolor/256x256/mimetypes/gnome-mime-application-pdf.png
