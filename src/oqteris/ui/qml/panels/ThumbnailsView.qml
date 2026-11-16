import QtQuick
import QtQuick.Controls.Basic
import "../themes"

ListView {
    id: root
    spacing: 12
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    model: pdfController.pageCount

    delegate: Item {
        id: thumbDelegate
        width: root.width - 24
        height: thumbImage.height + 24
        anchors.horizontalCenter: parent.horizontalCenter

        readonly property bool isCurrent: pdfController.currentPage === index

        Rectangle {
            anchors.fill: parent
            color: isCurrent ? Theme.selectedBackground : (mouseArea.containsMouse ? Theme.buttonHover : "transparent")
            border.color: isCurrent ? Theme.brandPrimary : Theme.borderSubtle
            border.width: isCurrent ? 2 : 1
            radius: 4

            Column {
                anchors.centerIn: parent
                spacing: 4

                Image {
                    id: thumbImage
                    width: root.width - 40
                    height: width * 1.35
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                    cache: false
                    source: pdfController.hasDocument ?
                        ("image://pdf/" + pdfController.activeDocId + "/" + index + "?thumb=1&v=" + pdfController.renderNonce) : ""
                }

                Text {
                    text: (index + 1).toString()
                    font.pixelSize: Theme.fontSizeSmall
                    font.family: Theme.fontFamily
                    color: isCurrent ? Theme.brandPrimary : Theme.textSecondary
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }

            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: pdfController.goToPage(index)
            }
        }
    }
}
