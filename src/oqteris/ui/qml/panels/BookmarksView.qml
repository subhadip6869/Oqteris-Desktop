import QtQuick
import QtQuick.Controls.Basic
import "../themes"

ListView {
    id: root
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    spacing: 2

    model: pdfController.tableOfContents

    delegate: Rectangle {
        width: root.width - 16
        height: 28
        anchors.horizontalCenter: parent.horizontalCenter
        color: mouseArea.containsMouse ? Theme.buttonHover : "transparent"
        radius: 3

        Row {
            anchors.fill: parent
            anchors.leftMargin: (modelData.level - 1) * 14 + 6
            anchors.rightMargin: 6
            spacing: 6

            Text {
                text: "📑"
                font.pixelSize: 12
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: modelData.title
                font.pixelSize: Theme.fontSizeNormal
                font.family: Theme.fontFamily
                color: Theme.textPrimary
                elide: Text.ElideRight
                width: parent.width - 60
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: "p. " + (modelData.pageIndex + 1)
                font.pixelSize: Theme.fontSizeSmall
                font.family: Theme.fontFamily
                color: Theme.textSecondary
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: pdfController.goToPage(modelData.pageIndex)
        }
    }

    Text {
        anchors.centerIn: parent
        text: "No bookmarks in document"
        color: Theme.textSecondary
        font.pixelSize: Theme.fontSizeNormal
        visible: root.count === 0
    }
}
