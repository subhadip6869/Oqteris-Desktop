import QtQuick
import QtQuick.Controls
import "../components"
import "../themes"

Item {
    id: root

    property var pageAnnotations: []

    function refresh() {
        if (pdfController.hasDocument) {
            pageAnnotations = annotationController.getAnnotations(pdfController.currentPage)
        } else {
            pageAnnotations = []
        }
    }

    Connections {
        target: pdfController
        function onPageChanged() { root.refresh() }
        function onDocumentChanged() { root.refresh() }
    }

    Connections {
        target: annotationController
        function onAnnotationsChanged(pageIdx) {
            if (pageIdx === pdfController.currentPage) {
                root.refresh()
            }
        }
    }

    Component.onCompleted: root.refresh()

    Column {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        Text {
            text: "Page " + (pdfController.currentPage + 1) + " Annotations"
            font.pixelSize: Theme.fontSizeMedium
            font.weight: Font.DemiBold
            color: Theme.textPrimary
        }

        ListView {
            width: parent.width
            height: parent.height - 40
            clip: true
            spacing: 6
            model: root.pageAnnotations

            delegate: Rectangle {
                width: parent.width
                height: 52
                color: Theme.cardBackground
                border.color: Theme.borderSubtle
                radius: 4

                Row {
                    anchors.fill: parent
                    anchors.margins: 6
                    spacing: 8

                    Text {
                        text: {
                            switch (modelData.type) {
                                case "highlight": return "🖍"
                                case "underline": return "<u>U</u>"
                                case "strikeout": return "<s>S</s>"
                                case "note": return "📝"
                                case "ink": return "✒"
                                case "rectangle": return "▭"
                                case "circle": return "◯"
                                case "stamp": return "✔"
                                default: return "💬"
                            }
                        }
                        font.pixelSize: 16
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Column {
                        width: parent.width - 64
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            text: modelData.type.toUpperCase()
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.brandPrimary
                        }

                        Text {
                            text: modelData.content || (modelData.author ? "By " + modelData.author : "Annotation")
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textPrimary
                            elide: Text.ElideRight
                            width: parent.width
                        }
                    }

                    // Delete button
                    Rectangle {
                        width: 24
                        height: 24
                        radius: 3
                        color: delMouse.containsMouse ? (Theme.isDark ? "#381A1A" : "#FEE2E2") : "transparent"
                        anchors.verticalCenter: parent.verticalCenter

                        OqIcon {
                            anchors.centerIn: parent
                            name: "close"
                            size: 12
                            color: delMouse.containsMouse ? Theme.statusError : Theme.textSecondary
                        }

                        MouseArea {
                            id: delMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: annotationController.deleteAnnotation(pdfController.currentPage, parseInt(modelData.id))
                        }
                    }
                }
            }

            Text {
                anchors.centerIn: parent
                text: "No annotations on this page"
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeNormal
                visible: root.pageAnnotations.length === 0
            }
        }
    }
}
