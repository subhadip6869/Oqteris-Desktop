import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../themes"

Rectangle {
    id: root
    color: Theme.workspaceBackground

    property alias viewportWidth: viewContainer.width
    property alias viewportHeight: viewContainer.height

    Column {
        anchors.fill: parent

        // Top: Document Tab Bar (Multiple open documents)
        Rectangle {
            id: docTabBar
            width: parent.width
            height: 32
            color: Theme.windowBackground
            border.color: Theme.borderSubtle
            border.width: 1
            visible: pdfController.openTabs.length > 0

            Row {
                anchors.left: parent.left
                anchors.leftMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                spacing: 4

                Repeater {
                    model: pdfController.openTabs

                    Rectangle {
                        id: tabItem
                        width: Math.min(220, Math.max(90, tabTitle.implicitWidth + 56))
                        height: 28
                        radius: 3
                        color: (modelData.isActive === true || modelData.isActive === "True")
                            ? Theme.workspaceBackground
                            : (tabMouse.containsMouse ? Theme.buttonHover : "transparent")
                        border.color: (modelData.isActive === true || modelData.isActive === "True")
                            ? Theme.brandPrimary
                            : "transparent"
                        border.width: 1

                        // 1. Tab Body Click Area (Switch Tab on Left Click, Close on Middle Click)
                        MouseArea {
                            id: tabMouse
                            anchors.left: parent.left
                            anchors.right: closeBtnRect.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            acceptedButtons: Qt.LeftButton | Qt.MiddleButton
                            onClicked: (mouse) => {
                                if (mouse.button === Qt.MiddleButton) {
                                    pdfController.closeDocument(modelData.docId)
                                } else {
                                    pdfController.switchTab(modelData.docId)
                                }
                            }
                        }

                        // 2. Tab Icon and Title
                        Row {
                            anchors.left: parent.left
                            anchors.leftMargin: 8
                            anchors.right: closeBtnRect.left
                            anchors.rightMargin: 4
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 6

                            Text {
                                text: "📄"
                                font.pixelSize: 11
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                id: tabTitle
                                text: modelData.fileName + ((modelData.isModified === true || modelData.isModified === "True") ? " *" : "")
                                font.pixelSize: Theme.fontSizeSmall
                                font.family: Theme.fontFamily
                                font.weight: (modelData.isActive === true || modelData.isActive === "True") ? Font.DemiBold : Font.Normal
                                color: Theme.textPrimary
                                elide: Text.ElideMiddle
                                width: parent.width - 20
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        // 3. Dedicated Close Tab Button
                        Rectangle {
                            id: closeBtnRect
                            width: 18
                            height: 18
                            anchors.right: parent.right
                            anchors.rightMargin: 4
                            anchors.verticalCenter: parent.verticalCenter
                            radius: 3
                            z: 2
                            color: closeMouse.containsMouse ? Theme.buttonPressed : "transparent"

                            Text {
                                anchors.centerIn: parent
                                text: "✕"
                                font.pixelSize: 9
                                font.bold: true
                                color: closeMouse.containsMouse ? Theme.brandPrimary : Theme.textSecondary
                            }

                            MouseArea {
                                id: closeMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: (mouse) => {
                                    mouse.accepted = true
                                    pdfController.closeDocument(modelData.docId)
                                }
                            }
                        }
                    }
                }

                // Add File Button '+'
                Rectangle {
                    width: 24
                    height: 24
                    radius: 3
                    color: addMouse.containsMouse ? Theme.buttonHover : "transparent"
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        anchors.centerIn: parent
                        text: "+"
                        font.pixelSize: 14
                        color: Theme.textPrimary
                    }

                    MouseArea {
                        id: addMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: fileDialogLoader.openFile()
                    }
                }
            }
        }

        // Top: Signature Notification Status Bar
        Rectangle {
            id: signatureStatusBar
            width: parent.width
            implicitHeight: 38
            height: implicitHeight
            visible: pdfController.hasDocument && signatureController.hasSignatures
            color: signatureController.hasInvalid
                ? (appController.isDarkMode ? "#3E1818" : "#FFEBEE")
                : (signatureController.allValidAndTrusted
                    ? (appController.isDarkMode ? "#1B3320" : "#E8F5E9")
                    : (appController.isDarkMode ? "#332B15" : "#FFF8E1"))
            border.color: signatureController.hasInvalid
                ? Theme.statusError
                : (signatureController.allValidAndTrusted ? Theme.statusSuccess : Theme.statusWarning)
            border.width: 1

            RowLayout {
                id: statusRow
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 10

                // Left: Status Icon and Message (clicking opens signatures panel)
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Rectangle {
                        width: 22
                        height: 22
                        radius: 11
                        color: signatureController.hasInvalid
                            ? Theme.statusError
                            : (signatureController.allValidAndTrusted ? Theme.statusSuccess : Theme.statusWarning)

                        Text {
                            anchors.centerIn: parent
                            text: signatureController.hasInvalid ? "✕" : (signatureController.allValidAndTrusted ? "✓" : "?")
                            font.pixelSize: 13
                            font.bold: true
                            color: "#FFFFFF"
                        }
                    }

                    Text {
                        id: statusSummaryLabel
                        text: signatureController.statusSummary
                        font.pixelSize: Theme.fontSizeSmall
                        font.weight: Font.DemiBold
                        color: signatureController.hasInvalid
                            ? Theme.statusError
                            : (signatureController.allValidAndTrusted
                                ? (appController.isDarkMode ? "#A5D6A7" : "#1B5E20")
                                : (appController.isDarkMode ? "#FFE082" : "#B78103"))
                        Layout.fillWidth: true
                        elide: Text.ElideRight

                        ToolTip.visible: summaryMouse.containsMouse && statusSummaryLabel.truncated
                        ToolTip.text: statusSummaryLabel.text
                        ToolTip.delay: 300
                    }

                    MouseArea {
                        id: summaryMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            mainPanelState.showLeftPanel = true
                            mainPanelState.currentPanelTab = "signatures"
                        }
                    }
                }

                // Right: Action Buttons
                RowLayout {
                    spacing: 8
                    Layout.alignment: Qt.AlignVCenter

                    // "Trust Signer" shortcut button if untrusted
                    Rectangle {
                        Layout.preferredWidth: trustSignerText.implicitWidth + 18
                        Layout.preferredHeight: 26
                        radius: 3
                        visible: signatureController.hasUntrusted
                        color: trustSignerMouse.containsMouse ? Theme.brandPrimaryHover : Theme.brandPrimary

                        Row {
                            anchors.centerIn: parent
                            spacing: 4
                            Text { text: "🛡"; font.pixelSize: 11; color: "#FFFFFF" }
                            Text {
                                id: trustSignerText
                                text: "Trust Signer"
                                font.pixelSize: 11
                                font.bold: true
                                color: "#FFFFFF"
                            }
                        }

                        MouseArea {
                            id: trustSignerMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: signatureController.trustSignatureCertificate(0)
                        }
                    }

                    // "Signature Panel" button
                    Rectangle {
                        Layout.preferredWidth: sigPanelText.implicitWidth + 18
                        Layout.preferredHeight: 26
                        radius: 3
                        color: sigPanelMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                        border.color: Theme.borderSubtle
                        border.width: 1

                        Row {
                            anchors.centerIn: parent
                            spacing: 4
                            Text { text: "🔏"; font.pixelSize: 11 }
                            Text {
                                id: sigPanelText
                                text: "Signature Panel"
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: Theme.textPrimary
                            }
                        }

                        MouseArea {
                            id: sigPanelMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                mainPanelState.showLeftPanel = true
                                mainPanelState.currentPanelTab = "signatures"
                            }
                        }
                    }

                    // "Validate All" button
                    Rectangle {
                        Layout.preferredWidth: valAllText.implicitWidth + 18
                        Layout.preferredHeight: 26
                        radius: 3
                        color: valAllMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                        border.color: Theme.borderSubtle
                        border.width: 1

                        Row {
                            anchors.centerIn: parent
                            spacing: 4
                            Text { text: "🔄"; font.pixelSize: 10 }
                            Text {
                                id: valAllText
                                text: "Validate All"
                                font.pixelSize: 11
                                color: Theme.textPrimary
                            }
                        }

                        MouseArea {
                            id: valAllMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: signatureController.inspectSignatures()
                        }
                    }
                }
            }
        }

        // Center: Viewing Area or Welcome Screen
        Item {
            id: viewContainer
            width: parent.width
            height: parent.height - (docTabBar.visible ? 32 : 0) - (signatureStatusBar.visible ? 36 : 0) - statusBar.height

            // Welcome View (No document open)
            Item {
                id: welcomeView
                anchors.fill: parent
                visible: !pdfController.hasDocument

                Column {
                    anchors.centerIn: parent
                    spacing: 20
                    width: Math.min(parent.width - 40, 520)

                    Column {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 8

                        Text {
                            text: "Oqteris"
                            font.pixelSize: 32
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.brandPrimary
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: "Professional Cross-Platform PDF Reader & Editor"
                            font.pixelSize: Theme.fontSizeMedium
                            color: Theme.textSecondary
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }

                    Rectangle {
                        width: 140
                        height: 38
                        radius: 4
                        color: Theme.brandPrimary
                        anchors.horizontalCenter: parent.horizontalCenter

                        Row {
                            anchors.centerIn: parent
                            spacing: 8
                            Text { text: "📂"; font.pixelSize: 14; color: "#FFFFFF" }
                            Text {
                                text: "Open PDF"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: "#FFFFFF"
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: fileDialogLoader.openFile()
                        }
                    }

                    // Recent Files Box
                    Rectangle {
                        width: parent.width
                        height: 240
                        radius: 6
                        color: Theme.cardBackground
                        border.color: Theme.borderSubtle
                        border.width: 1
                        visible: appController.recentFiles.length > 0

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 8

                            Text {
                                text: "Recent Documents"
                                font.pixelSize: Theme.fontSizeNormal
                                font.weight: Font.DemiBold
                                color: Theme.textPrimary
                            }

                            ListView {
                                width: parent.width
                                height: parent.height - 30
                                clip: true
                                spacing: 4
                                model: appController.recentFiles

                                delegate: Rectangle {
                                    width: parent.width
                                    height: 32
                                    radius: 3
                                    color: rMouse.containsMouse ? Theme.buttonHover : "transparent"

                                    Row {
                                        anchors.fill: parent
                                        anchors.margins: 4
                                        spacing: 8

                                        Text { text: "📄"; font.pixelSize: 12; anchors.verticalCenter: parent.verticalCenter }

                                        Text {
                                            text: modelData.fileName
                                            font.pixelSize: Theme.fontSizeSmall
                                            font.weight: Font.DemiBold
                                            color: modelData.isMissing ? Theme.textDisabled : Theme.textPrimary
                                            elide: Text.ElideRight
                                            width: parent.width - 140
                                            anchors.verticalCenter: parent.verticalCenter
                                        }

                                        Text {
                                            text: modelData.lastOpened
                                            font.pixelSize: 10
                                            color: Theme.textSecondary
                                            anchors.verticalCenter: parent.verticalCenter
                                        }
                                    }

                                    MouseArea {
                                        id: rMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: pdfController.openDocument(modelData.filePath)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // PDF Canvas Switcher
            Loader {
                anchors.fill: parent
                visible: pdfController.hasDocument
                source: pdfController.displayMode === "single" ? "SinglePageView.qml" : "ContinuousView.qml"
            }
        }

        // Bottom: Status Bar
        Rectangle {
            id: statusBar
            width: parent.width
            height: 30
            color: Theme.windowBackground
            border.color: Theme.borderSubtle
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12

                // Left: Page Navigation Controls
                Row {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 6
                    visible: pdfController.hasDocument

                    OqToolButton {
                        iconSymbol: "⏮"
                        tooltipText: "First Page"
                        enabled: pdfController.currentPage > 0
                        onClicked: pdfController.firstPage()
                    }

                    OqToolButton {
                        iconSymbol: "◀"
                        tooltipText: "Previous Page"
                        enabled: pdfController.currentPage > 0
                        onClicked: pdfController.prevPage()
                    }

                    Text {
                        text: "Page " + (pdfController.currentPage + 1) + " of " + pdfController.pageCount
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    OqToolButton {
                        iconSymbol: "▶"
                        tooltipText: "Next Page"
                        enabled: pdfController.currentPage < pdfController.pageCount - 1
                        onClicked: pdfController.nextPage()
                    }

                    OqToolButton {
                        iconSymbol: "⏭"
                        tooltipText: "Last Page"
                        enabled: pdfController.currentPage < pdfController.pageCount - 1
                        onClicked: pdfController.lastPage()
                    }
                }

                // Spacer
                Item {
                    width: 1
                    height: 1
                    Layout.fillWidth: true
                }

                // Right: Zoom and Display Controls
                Row {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8
                    visible: pdfController.hasDocument

                    OqToolButton {
                        iconSymbol: "🔍-"
                        tooltipText: "Zoom Out"
                        onClicked: pdfController.zoomOut()
                    }

                    Slider {
                        id: zoomSlider
                        width: 100
                        from: 0.2
                        to: 3.0
                        value: pdfController.zoomLevel
                        anchors.verticalCenter: parent.verticalCenter
                        onMoved: pdfController.setZoom(value)
                    }

                    OqToolButton {
                        iconSymbol: "🔍+"
                        tooltipText: "Zoom In"
                        onClicked: pdfController.zoomIn()
                    }

                    Text {
                        text: Math.round(pdfController.zoomLevel * 100) + "%"
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        width: 40
                        horizontalAlignment: Text.AlignRight
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Rectangle { width: 1; height: 16; color: Theme.divider; anchors.verticalCenter: parent.verticalCenter }

                    OqToolButton {
                        iconSymbol: "↔"
                        tooltipText: "Fit to Width"
                        onClicked: pdfController.fitWidth(viewContainer.width)
                    }

                    OqToolButton {
                        iconSymbol: "↕"
                        tooltipText: "Fit Entire Page"
                        onClicked: pdfController.fitPage(viewContainer.width, viewContainer.height)
                    }
                }
            }
        }
    }
}
