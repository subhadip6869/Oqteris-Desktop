import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../themes"

Rectangle {
    id: homeRoot
    color: appController.isDarkMode ? "#0F1115" : "#F4F7FB"

    property string filterQuery: ""

    // Filter recent files list based on user search query
    property var filteredRecentFiles: {
        var all = appController.recentFiles;
        if (!all || all.length === 0) return [];
        var q = filterQuery.trim().toLowerCase();
        if (!q) return all;
        return all.filter(function(item) {
            var nameMatch = item.fileName && item.fileName.toLowerCase().indexOf(q) !== -1;
            var pathMatch = item.filePath && item.filePath.toLowerCase().indexOf(q) !== -1;
            return nameMatch || pathMatch;
        });
    }

    // Top-level DropArea allowing PDFs dropped anywhere on the home screen
    DropArea {
        anchors.fill: parent
        onDropped: (drop) => {
            if (drop.hasUrls && drop.urls.length > 0) {
                for (var i = 0; i < drop.urls.length; i++) {
                    var rawUrl = drop.urls[i].toString();
                    var cleanPath = decodeURIComponent(rawUrl.replace(/^(file:\/{3}|file:\/\/)/, ""));
                    if (cleanPath.toLowerCase().endsWith(".pdf")) {
                        pdfController.openDocument(cleanPath);
                        drop.acceptProposedAction();
                        break;
                    }
                }
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: 24
        anchors.leftMargin: 36
        anchors.rightMargin: 36
        anchors.bottomMargin: 16
        spacing: 24

        // ==========================================
        // 1. App Header Banner (Icon + Title + Subtitle)
        // ==========================================
        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            // App Logo
            Image {
                Layout.preferredWidth: 54
                Layout.preferredHeight: 54
                source: appController.logoPath
                fillMode: Image.PreserveAspectFit
                mipmap: true
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                // Name and Version Pill
                RowLayout {
                    spacing: 10

                    Text {
                        text: appController.appName
                        font.pixelSize: 26
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: appController.isDarkMode ? "#F1F5F9" : "#1E293B"
                    }

                    Rectangle {
                        Layout.preferredHeight: 20
                        Layout.preferredWidth: versionText.implicitWidth + 14
                        radius: 10
                        color: "#2563EB"

                        Text {
                            id: versionText
                            anchors.centerIn: parent
                            text: "v" + appController.appVersion
                            font.pixelSize: 11
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: "#FFFFFF"
                        }
                    }
                }

                // Subtitle
                Text {
                    text: "Dedicated PDF Reader and Editor – Viewing, Annotation & Digital Signatures"
                    font.pixelSize: 13
                    font.family: Theme.fontFamily
                    color: appController.isDarkMode ? "#94A3B8" : "#64748B"
                }
            }
        }

        // ==========================================
        // 2. Main Two-Column Content Layout
        // ==========================================
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 28

            // ------------------------------------------
            // Left Column: Actions (Width: 310)
            // ------------------------------------------
            ColumnLayout {
                Layout.preferredWidth: 210
                Layout.fillHeight: true
                spacing: 12

                Text {
                    text: "Actions"
                    font.pixelSize: 15
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: appController.isDarkMode ? "#F1F5F9" : "#0F172A"
                    Layout.bottomMargin: 4
                }

                // Action Card 1: Open PDF Document...
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 64
                    radius: 10
                    color: openMouse.containsMouse ? (appController.isDarkMode ? "#252830" : "#F8FAFC") : (appController.isDarkMode ? "#1B1D22" : "#FFFFFF")
                    border.color: openMouse.containsMouse ? "#3B82F6" : (appController.isDarkMode ? "#2F333B" : "#E2E8F0")
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 14
                        spacing: 12

                        // Icon Box (Blue)
                        Rectangle {
                            Layout.preferredWidth: 40
                            Layout.preferredHeight: 40
                            radius: 8
                            color: "#2563EB"

                            Canvas {
                                id: docIconCanvas
                                anchors.centerIn: parent
                                width: 18
                                height: 22
                                onPaint: {
                                    var ctx = getContext("2d");
                                    ctx.reset();
                                    ctx.strokeStyle = "#FFFFFF";
                                    ctx.lineWidth = 1.6;
                                    var w = width, h = height, c = 5;
                                    ctx.beginPath();
                                    ctx.moveTo(1, 1);
                                    ctx.lineTo(w - c, 1);
                                    ctx.lineTo(w - 1, c);
                                    ctx.lineTo(w - 1, h - 1);
                                    ctx.lineTo(1, h - 1);
                                    ctx.closePath();
                                    ctx.stroke();

                                    ctx.beginPath();
                                    ctx.moveTo(w - c, 1);
                                    ctx.lineTo(w - c, c);
                                    ctx.lineTo(w - 1, c);
                                    ctx.stroke();

                                    ctx.beginPath();
                                    ctx.moveTo(4, 9); ctx.lineTo(w - 4, 9);
                                    ctx.moveTo(4, 13); ctx.lineTo(w - 4, 13);
                                    ctx.moveTo(4, 17); ctx.lineTo(w - 6, 17);
                                    ctx.stroke();
                                }
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: "Open PDF Document..."
                                font.pixelSize: 13
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: "#2563EB"
                            }

                            Text {
                                text: "Browse your system to view or edit a PDF"
                                font.pixelSize: 11
                                font.family: Theme.fontFamily
                                color: appController.isDarkMode ? "#94A3B8" : "#64748B"
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                    }

                    MouseArea {
                        id: openMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: fileDialogLoader.openFile()
                    }
                }

                // Action Card 2: Security & Trust Store
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 64
                    radius: 10
                    color: secMouse.containsMouse ? (appController.isDarkMode ? "#252830" : "#F8FAFC") : (appController.isDarkMode ? "#1B1D22" : "#FFFFFF")
                    border.color: secMouse.containsMouse ? "#10B981" : (appController.isDarkMode ? "#2F333B" : "#E2E8F0")
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 14
                        spacing: 12

                        // Icon Box (Green)
                        Rectangle {
                            Layout.preferredWidth: 40
                            Layout.preferredHeight: 40
                            radius: 8
                            color: "#059669"

                            Canvas {
                                id: shieldIconCanvas
                                anchors.centerIn: parent
                                width: 20
                                height: 22
                                onPaint: {
                                    var ctx = getContext("2d");
                                    ctx.reset();
                                    ctx.strokeStyle = "#FFFFFF";
                                    ctx.lineWidth = 1.8;
                                    ctx.lineCap = "round";
                                    ctx.lineJoin = "round";

                                    var w = width, h = height;
                                    ctx.beginPath();
                                    ctx.moveTo(w / 2, 1);
                                    ctx.lineTo(w - 1, 4.5);
                                    ctx.quadraticCurveTo(w - 1, h * 0.65, w / 2, h - 1);
                                    ctx.quadraticCurveTo(1, h * 0.65, 1, 4.5);
                                    ctx.closePath();
                                    ctx.stroke();

                                    ctx.beginPath();
                                    ctx.moveTo(5.5, 11);
                                    ctx.lineTo(8.5, 14.5);
                                    ctx.lineTo(14.5, 7.5);
                                    ctx.stroke();
                                }
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: "Security & Trust Store"
                                font.pixelSize: 13
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: "#059669"
                            }

                            Text {
                                text: "Manage certificates and digital signature trust levels"
                                font.pixelSize: 11
                                font.family: Theme.fontFamily
                                color: appController.isDarkMode ? "#94A3B8" : "#64748B"
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                    }

                    MouseArea {
                        id: secMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: trustStoreDialogLoader.openTrustStoreDialog()
                    }
                }

                // Action Card 3: Application Settings
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 64
                    radius: 10
                    color: setMouse.containsMouse ? (appController.isDarkMode ? "#252830" : "#F8FAFC") : (appController.isDarkMode ? "#1B1D22" : "#FFFFFF")
                    border.color: setMouse.containsMouse ? "#6366F1" : (appController.isDarkMode ? "#2F333B" : "#E2E8F0")
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 14
                        spacing: 12

                        // Icon Box (Purple/Indigo)
                        Rectangle {
                            Layout.preferredWidth: 40
                            Layout.preferredHeight: 40
                            radius: 8
                            color: "#6366F1"

                            Text {
                                anchors.centerIn: parent
                                text: "⚙"
                                font.pixelSize: 22
                                color: "#FFFFFF"
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: "Application Settings"
                                font.pixelSize: 13
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: "#6366F1"
                            }

                            Text {
                                text: "Configure default author, theme, and default viewer"
                                font.pixelSize: 11
                                font.family: Theme.fontFamily
                                color: appController.isDarkMode ? "#94A3B8" : "#64748B"
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                    }

                    MouseArea {
                        id: setMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: settingsDialogLoader.openSettingsDialog()
                    }
                }

                // Action Card 4: Drag & Drop Zone (Dashed Border)
                Item {
                    id: dropZoneItem
                    Layout.fillWidth: true
                    Layout.preferredHeight: 110
                    Layout.topMargin: 4

                    property bool isHovered: dropZoneMouse.containsMouse || dropZoneArea.containsDrag

                    Rectangle {
                        anchors.fill: parent
                        radius: 10
                        color: dropZoneItem.isHovered ? (appController.isDarkMode ? "#202636" : "#EFF6FF") : (appController.isDarkMode ? "#16181D" : "#F8FAFC")
                    }

                    // Dashed Border Canvas
                    Canvas {
                        id: dashedCanvas
                        anchors.fill: parent
                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.reset();
                            ctx.strokeStyle = dropZoneItem.isHovered ? "#3B82F6" : (appController.isDarkMode ? "#4B5563" : "#CBD5E1");
                            ctx.lineWidth = 1.5;
                            ctx.setLineDash([5, 4]);

                            var r = 10;
                            var w = width;
                            var h = height;

                            ctx.beginPath();
                            ctx.moveTo(r, 0.75);
                            ctx.lineTo(w - r, 0.75);
                            ctx.quadraticCurveTo(w - 0.75, 0.75, w - 0.75, r);
                            ctx.lineTo(w - 0.75, h - r);
                            ctx.quadraticCurveTo(w - 0.75, h - 0.75, w - r, h - 0.75);
                            ctx.lineTo(r, h - 0.75);
                            ctx.quadraticCurveTo(0.75, h - 0.75, 0.75, h - r);
                            ctx.lineTo(0.75, r);
                            ctx.quadraticCurveTo(0.75, 0.75, r, 0.75);
                            ctx.closePath();
                            ctx.stroke();
                        }
                        onWidthChanged: requestPaint()
                        onHeightChanged: requestPaint()
                        Connections {
                            target: dropZoneItem
                            function onIsHoveredChanged() { dashedCanvas.requestPaint() }
                        }
                    }

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 6

                        // Folder Icon Outline
                        Canvas {
                            Layout.alignment: Qt.AlignHCenter
                            width: 28
                            height: 22
                            onPaint: {
                                var ctx = getContext("2d");
                                ctx.reset();
                                ctx.strokeStyle = dropZoneItem.isHovered ? "#3B82F6" : "#64748B";
                                ctx.lineWidth = 1.8;
                                ctx.lineCap = "round";
                                ctx.lineJoin = "round";

                                var w = width, h = height;
                                ctx.beginPath();
                                ctx.moveTo(2, 6);
                                ctx.lineTo(9, 6);
                                ctx.lineTo(12, 9);
                                ctx.lineTo(w - 2, 9);
                                ctx.lineTo(w - 2, h - 2);
                                ctx.lineTo(2, h - 2);
                                ctx.closePath();
                                ctx.stroke();
                            }
                            Connections {
                                target: dropZoneItem
                                function onIsHoveredChanged() { requestPaint() }
                            }
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Drag & drop a PDF here"
                            font.pixelSize: 13
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: dropZoneItem.isHovered ? "#2563EB" : (appController.isDarkMode ? "#E2E8F0" : "#334155")
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "or click to browse files"
                            font.pixelSize: 11
                            font.family: Theme.fontFamily
                            color: appController.isDarkMode ? "#94A3B8" : "#64748B"
                        }
                    }

                    DropArea {
                        id: dropZoneArea
                        anchors.fill: parent
                        onDropped: (drop) => {
                            if (drop.hasUrls && drop.urls.length > 0) {
                                for (var i = 0; i < drop.urls.length; i++) {
                                    var rawUrl = drop.urls[i].toString();
                                    var cleanPath = decodeURIComponent(rawUrl.replace(/^(file:\/{3}|file:\/\/)/, ""));
                                    if (cleanPath.toLowerCase().endsWith(".pdf")) {
                                        pdfController.openDocument(cleanPath);
                                        drop.acceptProposedAction();
                                        break;
                                    }
                                }
                            }
                        }
                    }

                    MouseArea {
                        id: dropZoneMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: fileDialogLoader.openFile()
                    }
                }

                // Vertical filler spacer to keep actions aligned to top
                Item {
                    Layout.fillHeight: true
                }
            }

            // ------------------------------------------
            // Right Column: Recent PDF Documents
            // ------------------------------------------
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 12

                // Header Row (Title + Filter Search + Clear History)
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Text {
                        text: "Recent PDF Documents"
                        font.pixelSize: 15
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: appController.isDarkMode ? "#F1F5F9" : "#0F172A"
                        Layout.alignment: Qt.AlignVCenter
                    }

                    Item { Layout.fillWidth: true }

                    // Search Filter Box
                    Rectangle {
                        Layout.preferredWidth: 200
                        Layout.preferredHeight: 30
                        radius: 6
                        color: appController.isDarkMode ? "#1B1D22" : "#FFFFFF"
                        border.color: filterInput.activeFocus ? "#2563EB" : "#93C5FD"
                        border.width: 1.5

                        TextInput {
                            id: filterInput
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            verticalAlignment: TextInput.AlignVCenter
                            font.pixelSize: 11
                            font.family: Theme.fontFamily
                            color: appController.isDarkMode ? "#F1F5F9" : "#0F172A"
                            clip: true
                            onTextChanged: homeRoot.filterQuery = text

                            Text {
                                text: "Filter recent PDFs..."
                                visible: !filterInput.text && !filterInput.activeFocus
                                anchors.fill: parent
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 11
                                font.family: Theme.fontFamily
                                color: appController.isDarkMode ? "#64748B" : "#94A3B8"
                            }
                        }
                    }

                    // Clear History Button
                    Rectangle {
                        Layout.preferredWidth: clearHistoryText.implicitWidth + 20
                        Layout.preferredHeight: 30
                        radius: 6
                        color: clearMouse.containsMouse ? (appController.isDarkMode ? "#2D3036" : "#E2E8F0") : (appController.isDarkMode ? "#1B1D22" : "#F8FAFC")
                        border.color: appController.isDarkMode ? "#383C44" : "#CBD5E1"
                        border.width: 1

                        Text {
                            id: clearHistoryText
                            anchors.centerIn: parent
                            text: "Clear History"
                            font.pixelSize: 11
                            font.family: Theme.fontFamily
                            color: appController.isDarkMode ? "#D4D4D8" : "#334155"
                        }

                        MouseArea {
                            id: clearMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: appController.clearRecentFiles()
                        }
                    }
                }

                // Recent Files ListView
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "transparent"
                    clip: true

                    ListView {
                        id: recentListView
                        anchors.fill: parent
                        spacing: 8
                        model: homeRoot.filteredRecentFiles

                        delegate: Rectangle {
                            id: itemCard
                            width: recentListView.width
                            height: 52
                            radius: 8
                            color: itemMouse.containsMouse ? (appController.isDarkMode ? "#242730" : "#F8FAFC") : (appController.isDarkMode ? "#181A1F" : "#FFFFFF")
                            border.color: itemMouse.containsMouse ? "#CBD5E1" : (appController.isDarkMode ? "#2E323A" : "#E2E8F0")
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 14
                                anchors.rightMargin: 16
                                spacing: 12

                                // Red "PDF" Badge
                                Rectangle {
                                    Layout.preferredWidth: 34
                                    Layout.preferredHeight: 22
                                    radius: 4
                                    color: "#DC2626"

                                    Text {
                                        anchors.centerIn: parent
                                        text: "PDF"
                                        font.pixelSize: 10
                                        font.bold: true
                                        font.family: Theme.fontFamily
                                        color: "#FFFFFF"
                                    }
                                }

                                // Title and Path
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        text: modelData.fileName
                                        font.pixelSize: 13
                                        font.bold: true
                                        font.family: Theme.fontFamily
                                        color: modelData.isMissing ? Theme.textDisabled : (appController.isDarkMode ? "#F1F5F9" : "#0F172A")
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }

                                    Text {
                                        text: modelData.filePath
                                        font.pixelSize: 11
                                        font.family: Theme.fontFamily
                                        color: appController.isDarkMode ? "#94A3B8" : "#64748B"
                                        elide: Text.ElideMiddle
                                        Layout.fillWidth: true
                                    }
                                }

                                // Timestamp
                                Text {
                                    text: modelData.lastOpened
                                    font.pixelSize: 11
                                    font.family: Theme.fontFamily
                                    color: appController.isDarkMode ? "#64748B" : "#94A3B8"
                                    Layout.alignment: Qt.AlignVCenter
                                }
                            }

                            MouseArea {
                                id: itemMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: pdfController.openDocument(modelData.filePath)
                            }
                        }

                        // Empty State if no recent files or no search matches
                        Item {
                            anchors.centerIn: parent
                            width: parent.width
                            height: 120
                            visible: !homeRoot.filteredRecentFiles || homeRoot.filteredRecentFiles.length === 0

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 8

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: filterInput.text.trim() ? "No recent documents match your filter." : "No recent PDF documents."
                                    font.pixelSize: 13
                                    font.family: Theme.fontFamily
                                    color: appController.isDarkMode ? "#94A3B8" : "#64748B"
                                }

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: filterInput.text.trim() ? "Try clearing the search filter." : "Open a PDF document to see it listed here."
                                    font.pixelSize: 11
                                    font.family: Theme.fontFamily
                                    color: appController.isDarkMode ? "#64748B" : "#94A3B8"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
