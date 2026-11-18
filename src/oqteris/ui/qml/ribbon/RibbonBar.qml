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

        // Top: Ribbon Tabs Header Bar
        Rectangle {
            id: tabBar
            width: parent.width
            height: 32
            color: Theme.windowBackground

            Row {
                anchors.left: parent.left
                anchors.leftMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                spacing: 2

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
