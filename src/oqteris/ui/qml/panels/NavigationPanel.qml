import QtQuick
import "../components"
import "../themes"

Rectangle {
    id: root
    width: 280
    color: Theme.panelBackground
    border.color: Theme.borderSubtle
    border.width: 1

    Row {
        anchors.fill: parent

        // Left Icon Bar (Switcher)
        Rectangle {
            width: 44
            height: parent.height
            color: Theme.windowBackground
            border.color: Theme.borderSubtle
            border.width: 1

            Column {
                anchors.top: parent.top
                anchors.topMargin: 8
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 6

                Repeater {
                    model: [
                        { id: "thumbnails", icon: "🖼", tip: "Thumbnails" },
                        { id: "bookmarks", icon: "📑", tip: "Bookmarks" },
                        { id: "annotations", icon: "💬", tip: "Annotations" },
                        { id: "signatures", icon: "🔏", tip: "Signatures" },
                        { id: "search", icon: "🔎", tip: "Search" }
                    ]

                    Rectangle {
                        width: 32
                        height: 32
                        radius: 4
                        color: {
                            if (mainPanelState.currentPanelTab === modelData.id) return Theme.selectedBackground
                            if (mArea.containsMouse) return Theme.buttonHover
                            return "transparent"
                        }
                        border.color: mainPanelState.currentPanelTab === modelData.id ? Theme.brandPrimary : "transparent"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: modelData.icon
                            font.pixelSize: 14
                        }

                        MouseArea {
                            id: mArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                mainPanelState.currentPanelTab = modelData.id
                                if (modelData.id === "signatures") {
                                    signatureController.inspectSignatures()
                                }
                            }
                        }
                    }
                }
            }
        }

        // Active Panel Content
        Item {
            width: parent.width - 44
            height: parent.height

            Loader {
                id: panelContentLoader
                anchors.fill: parent
                source: {
                    switch (mainPanelState.currentPanelTab) {
                        case "thumbnails": return "ThumbnailsView.qml"
                        case "bookmarks": return "BookmarksView.qml"
                        case "annotations": return "AnnotationsView.qml"
                        case "signatures": return "SignaturesView.qml"
                        case "search": return "SearchView.qml"
                        default: return "ThumbnailsView.qml"
                    }
                }
            }
        }
    }
}
