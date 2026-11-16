Name:           oqteris
Version:        1.0.0
Release:        1%{?dist}
Summary:        Complete Cross-Platform PDF Reader and Editor
License:        Apache-2.0
URL:            https://originsd.vercel.app
Source0:        %{name}-%{version}.tar.gz

Requires:       qt6-qtbase-gui, qt6-qtdeclarative, tesseract

%description
Oqteris is a dedicated desktop PDF reader and editor built using Python 3.13+
and Qt Quick/QML. Features high-performance PyMuPDF rendering, pikepdf structural
manipulation, pyHanko cryptographic signature validation, and OCR integration.

%prep
%setup -q

%build
# Build standalone package

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps
install -m 755 dist/Oqteris %{buildroot}/usr/bin/oqteris
install -m 644 packaging/linux/app.vercel.originsd.oqteris.desktop %{buildroot}/usr/share/applications/
install -m 644 assets/icons/app/oqteris-logo.png %{buildroot}/usr/share/icons/hicolor/scalable/apps/app.vercel.originsd.oqteris.png

%files
/usr/bin/oqteris
/usr/share/applications/app.vercel.originsd.oqteris.desktop
/usr/share/icons/hicolor/scalable/apps/app.vercel.originsd.oqteris.png
