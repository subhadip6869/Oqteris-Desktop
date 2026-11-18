import QtQuick
import "../components"
import "../themes"

Rectangle {
    id: root

    implicitHeight: 124
    color: Theme.ribbonBackground
    border.color: Theme.borderSubtle
    border.width: 1

    Column {
        anchors.fill: parent

        // Top: Ribbon Tabs Header Bar (Native Desktop Ribbon Header)
        Rectangle {
            id: tabBar
            width: parent.width
            height: 34
            color: Theme.windowBackground

            // Left: Quick Action Tools + Ribbon Tabs
            Row {
                anchors.left: parent.left
                anchors.leftMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                spacing: 3

                // Quick Action Buttons
                OqToolButton {
                    iconName: "folder-open"
                    tooltipText: "Open Document"
                    shortcutText: "Ctrl+O"
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: fileDialogLoader.openFile()
                }

                OqToolButton {
                    iconName: "save"
                    tooltipText: "Save Document"
                    shortcutText: "Ctrl+S"
                    enabled: pdfController.hasDocument && pdfController.isModified
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: pdfController.saveDocument()
                }

                OqToolButton {
                    iconName: "undo"
                    tooltipText: "Undo"
                    shortcutText: "Ctrl+Z"
                    enabled: ribbonController.canUndo
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: ribbonController.undo()
                }

                OqToolButton {
                    iconName: "redo"
                    tooltipText: "Redo"
                    shortcutText: "Ctrl+Y"
                    enabled: ribbonController.canRedo
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: ribbonController.redo()
                }

                Rectangle {
                    width: 1
                    height: 16
                    color: Theme.divider
                    anchors.verticalCenter: parent.verticalCenter
                }

                // Ribbon Tabs
                OqTabButton {
                    text: "Home"
                    isSelected: ribbonController.currentTab === "Home"
                    onClicked: ribbonController.selectTab("Home")
                }

                OqTabButton {
                    text: "View"
                    isSelected: ribbonController.currentTab === "View"
                    onClicked: ribbonController.selectTab("View")
                }

                OqTabButton {
                    text: "Edit"
                    isSelected: ribbonController.currentTab === "Edit"
                    onClicked: ribbonController.selectTab("Edit")
                }

                OqTabButton {
                    text: "Comment"
                    isSelected: ribbonController.currentTab === "Comment"
                    onClicked: ribbonController.selectTab("Comment")
                }

                OqTabButton {
                    text: "Organize"
                    isSelected: ribbonController.currentTab === "Organize"
                    onClicked: ribbonController.selectTab("Organize")
                }

                OqTabButton {
                    text: "Convert"
                    isSelected: ribbonController.currentTab === "Convert"
                    onClicked: ribbonController.selectTab("Convert")
                }

                OqTabButton {
                    text: "Fill & Sign"
                    isSelected: ribbonController.currentTab === "FillSign"
                    onClicked: ribbonController.selectTab("FillSign")
                }

                OqTabButton {
                    text: "Protect"
                    isSelected: ribbonController.currentTab === "Protect"
                    onClicked: ribbonController.selectTab("Protect")
                }

                OqTabButton {
                    text: "Share"
                    isSelected: ribbonController.currentTab === "Share"
                    onClicked: ribbonController.selectTab("Share")
                }

                OqTabButton {
                    text: "Help"
                    isSelected: ribbonController.currentTab === "Help"
                    onClicked: ribbonController.selectTab("Help")
                }
            }

            // Right header shortcuts (Default Viewer, Theme, Settings, About)
            Row {
                anchors.right: parent.right
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6

                // Default Viewer Pill
                Rectangle {
                    id: defaultPill
                    width: defaultPillText.implicitWidth + 14
                    height: 22
                    radius: 11
                    color: defaultPillMouse.containsMouse
                        ? (appController.isDarkMode ? "#1E3A8A" : "#DBEAFE")
                        : (appController.isDefaultViewer ? Theme.statusSuccess : Theme.selectedBackground)
                    visible: !appController.isDefaultViewer
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        id: defaultPillText
                        anchors.centerIn: parent
                        text: "Set as Default PDF Viewer"
                        font.pixelSize: 10
                        color: appController.isDarkMode ? "#93C5FD" : Theme.brandPrimary
                    }

                    MouseArea {
                        id: defaultPillMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: appController.requestMakeDefaultViewer()
                    }
                }

                OqToolButton {
                    anchors.verticalCenter: parent.verticalCenter
                    iconName: appController.isDarkMode ? "theme-light" : "theme-dark"
                    tooltipText: "Toggle Theme"
                    onClicked: appController.toggleTheme()
                }

                OqToolButton {
                    anchors.verticalCenter: parent.verticalCenter
                    iconName: "settings"
                    tooltipText: "Settings"
                    onClicked: settingsDialogLoader.openSettingsDialog()
                }

                OqToolButton {
                    anchors.verticalCenter: parent.verticalCenter
                    iconName: "properties"
                    tooltipText: "About Oqteris"
                    onClicked: aboutDialogLoader.openAboutDialog()
                }
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: Theme.divider
            }
        }

        // Bottom: Ribbon Command Groups Container
        Item {
            id: contentArea
            width: parent.width
            height: 90

            Flickable {
                anchors.fill: parent
                contentWidth: tabLoader.item ? tabLoader.item.implicitWidth : width
                contentHeight: height
                boundsBehavior: Flickable.StopAtBounds
                clip: true

                Loader {
                    id: tabLoader
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    source: {
                        switch (ribbonController.currentTab) {
                            case "Home": return "HomeTab.qml"
                            case "View": return "ViewTab.qml"
                            case "Edit": return "EditTab.qml"
                            case "Comment": return "CommentTab.qml"
                            case "Organize": return "OrganizeTab.qml"
                            case "Convert": return "ConvertTab.qml"
                            case "FillSign": return "FillSignTab.qml"
                            case "Protect": return "ProtectTab.qml"
                            case "Share": return "ShareTab.qml"
                            case "Help": return "HelpTab.qml"
                            default: return "HomeTab.qml"
                        }
                    }
                }
            }
        }
    }
}
