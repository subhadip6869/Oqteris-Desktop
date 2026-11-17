import QtQuick
import "../components"
import "../themes"

Rectangle {
    id: root
    width: 320
    color: Theme.panelBackground
    border.color: Theme.borderSubtle
    border.width: 1

    readonly property int minPanelWidth: 260
    readonly property int maxPanelWidth: 500

    Connections {
        target: signatureController
        function onSignaturesChanged() {
            if (signatureController.hasSignatures && !mainPanelState.showLeftPanel) {
                mainPanelState.showLeftPanel = true
                mainPanelState.currentPanelTab = "signatures"
            }
        }
    }

    // Left Icon Bar (Switcher)
    Rectangle {
        id: iconBar
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 44
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
        id: contentContainer
        anchors.left: iconBar.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

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

    // Right Splitter Drag Handle for resizing panel
    Rectangle {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 4
        z: 10
        color: resizeMouse.containsMouse || resizeMouse.pressed ? Theme.brandPrimary : "transparent"

        MouseArea {
            id: resizeMouse
            anchors.fill: parent
            anchors.leftMargin: -2
            anchors.rightMargin: -2
            hoverEnabled: true
            cursorShape: Qt.SizeHorCursor
            property int startX: 0
            property int startWidth: 0

            onPressed: (mouse) => {
                startX = mouse.x
                startWidth = root.width
            }

            onPositionChanged: (mouse) => {
                if (pressed) {
                    var delta = mouse.x - startX
                    var newW = root.width + delta
                    root.width = Math.max(root.minPanelWidth, Math.min(root.maxPanelWidth, newW))
                }
            }
        }
    }
}
