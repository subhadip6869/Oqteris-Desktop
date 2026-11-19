import QtQuick
import QtQuick.Controls
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

                            OqIcon {
                                anchors.centerIn: parent
                                name: "close"
                                size: 10
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
            implicitHeight: Math.max(38, statusRow.implicitHeight + 8)
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
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 26
                    Layout.alignment: Qt.AlignVCenter

                    RowLayout {
                        anchors.fill: parent
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
                            Layout.preferredWidth: 0
                            elide: Text.ElideRight
                        }
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

                    ToolTip.visible: summaryMouse.containsMouse && statusSummaryLabel.truncated
                    ToolTip.text: statusSummaryLabel.text
                    ToolTip.delay: 300
                }

                // Right: Action Buttons
                RowLayout {
                    spacing: 6
                    Layout.alignment: Qt.AlignVCenter

                    // "Trust Signer" shortcut button if untrusted
                    Rectangle {
                        Layout.preferredWidth: trustSignerRow.implicitWidth + 16
                        Layout.preferredHeight: 26
                        radius: 3
                        visible: signatureController.hasUntrusted
                        color: trustSignerMouse.containsMouse ? Theme.brandPrimaryHover : Theme.brandPrimary

                        Row {
                            id: trustSignerRow
                            anchors.centerIn: parent
                            spacing: 4
                            Text {
                                text: "🛡"
                                font.pixelSize: 11
                                color: "#FFFFFF"
                                visible: signatureStatusBar.width > 600
                            }
                            Text {
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
                        Layout.preferredWidth: sigPanelRow.implicitWidth + 16
                        Layout.preferredHeight: 26
                        radius: 3
                        color: sigPanelMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                        border.color: Theme.borderSubtle
                        border.width: 1

                        Row {
                            id: sigPanelRow
                            anchors.centerIn: parent
                            spacing: 4
                            Text {
                                text: "🔏"
                                font.pixelSize: 11
                                visible: signatureStatusBar.width > 660
                            }
                            Text {
                                text: signatureStatusBar.width > 520 ? "Signature Panel" : "Panel"
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
                        Layout.preferredWidth: valAllRow.implicitWidth + 16
                        Layout.preferredHeight: 26
                        radius: 3
                        color: valAllMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                        border.color: Theme.borderSubtle
                        border.width: 1

                        Row {
                            id: valAllRow
                            anchors.centerIn: parent
                            spacing: 4
                            Text { text: "🔄"; font.pixelSize: 10 }
                            Text {
                                text: signatureStatusBar.width > 480 ? "Validate All" : "Validate"
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
            height: parent.height - (docTabBar.visible ? 32 : 0) - (signatureStatusBar.visible ? signatureStatusBar.height : 0) - statusBar.height

            // Welcome / HomeScreen View (No document open)
            HomeScreen {
                id: homeScreen
                anchors.fill: parent
                visible: !pdfController.hasDocument
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

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 0

                // Left: Page Navigation Controls (When Document is open)
                RowLayout {
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 6
                    visible: pdfController.hasDocument

                    OqToolButton {
                        Layout.alignment: Qt.AlignVCenter
                        iconSymbol: "⏮"
                        tooltipText: "First Page"
                        enabled: pdfController.currentPage > 0
                        onClicked: pdfController.firstPage()
                    }

                    OqToolButton {
                        Layout.alignment: Qt.AlignVCenter
                        iconSymbol: "◀"
                        tooltipText: "Previous Page"
                        enabled: pdfController.currentPage > 0
                        onClicked: pdfController.prevPage()
                    }

                    Text {
                        Layout.alignment: Qt.AlignVCenter
                        text: "Page " + (pdfController.currentPage + 1) + " of " + pdfController.pageCount
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    OqToolButton {
                        Layout.alignment: Qt.AlignVCenter
                        iconSymbol: "▶"
                        tooltipText: "Next Page"
                        enabled: pdfController.currentPage < pdfController.pageCount - 1
                        onClicked: pdfController.nextPage()
                    }

                    OqToolButton {
                        Layout.alignment: Qt.AlignVCenter
                        iconSymbol: "⏭"
                        tooltipText: "Last Page"
                        enabled: pdfController.currentPage < pdfController.pageCount - 1
                        onClicked: pdfController.lastPage()
                    }
                }

                // Left: Status on Homescreen (When no Document is open)
                RowLayout {
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 16
                    visible: !pdfController.hasDocument

                    Text {
                        text: "Ready"
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                    }

                    Row {
                        spacing: 4
                        Text {
                            text: "•"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#10B981"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: "Autosaved"
                            font.pixelSize: 11
                            font.family: Theme.fontFamily
                            color: "#059669"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }

                // Flexible Spacer
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }

                // Right: Zoom and Display Controls
                RowLayout {
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 6

                    OqToolButton {
                        Layout.alignment: Qt.AlignVCenter
                        iconSymbol: "-"
                        tooltipText: "Zoom Out"
                        onClicked: pdfController.zoomOut()
                    }

                    Slider {
                        id: zoomSlider
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: 100
                        Layout.preferredHeight: 20
                        hoverEnabled: true
                        from: 0.2
                        to: 3.0
                        value: pdfController.zoomLevel
                        onMoved: pdfController.setZoom(value)

                        background: Rectangle {
                            x: zoomSlider.leftPadding
                            y: zoomSlider.topPadding + zoomSlider.availableHeight / 2 - height / 2
                            implicitWidth: 100
                            implicitHeight: 4
                            width: zoomSlider.availableWidth
                            height: 4
                            radius: 2
                            color: appController.isDarkMode ? "#3E3E42" : "#D0D0D0"

                            Rectangle {
                                width: zoomSlider.visualPosition * parent.width
                                height: parent.height
                                color: Theme.brandPrimary
                                radius: 2
                            }
                        }

                        handle: Rectangle {
                            x: zoomSlider.leftPadding + zoomSlider.visualPosition * (zoomSlider.availableWidth - width)
                            y: zoomSlider.topPadding + zoomSlider.availableHeight / 2 - height / 2
                            implicitWidth: 12
                            implicitHeight: 12
                            radius: 6
                            color: zoomSlider.pressed ? Theme.brandPrimaryHover : (zoomSlider.hovered ? "#FFFFFF" : (appController.isDarkMode ? "#E0E0E0" : "#FFFFFF"))
                            border.color: zoomSlider.pressed || zoomSlider.hovered ? Theme.brandPrimary : (appController.isDarkMode ? "#777777" : "#A0A0A0")
                            border.width: 1.5
                        }
                    }

                    OqToolButton {
                        Layout.alignment: Qt.AlignVCenter
                        iconSymbol: "+"
                        tooltipText: "Zoom In"
                        onClicked: pdfController.zoomIn()
                    }

                    Text {
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: 42
                        text: Math.round(pdfController.zoomLevel * 100) + "%"
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        horizontalAlignment: Text.AlignRight
                    }

                    Rectangle {
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: 1
                        Layout.preferredHeight: 16
                        color: Theme.divider
                        visible: pdfController.hasDocument
                    }

                    OqToolButton {
                        Layout.alignment: Qt.AlignVCenter
                        iconSymbol: "↔"
                        tooltipText: "Fit to Width"
                        visible: pdfController.hasDocument
                        onClicked: pdfController.fitWidth(viewContainer.width)
                    }

                    OqToolButton {
                        Layout.alignment: Qt.AlignVCenter
                        iconSymbol: "↕"
                        tooltipText: "Fit Entire Page"
                        visible: pdfController.hasDocument
                        onClicked: pdfController.fitPage(viewContainer.width, viewContainer.height)
                    }
                }
            }
        }
    }
}
