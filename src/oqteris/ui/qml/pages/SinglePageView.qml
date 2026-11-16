import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Flickable {
    id: root
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    contentWidth: Math.max(width, paperSheet.width + 40)
    contentHeight: Math.max(height, paperSheet.height + 40)

    Rectangle {
        id: paperSheet
        x: Math.max(20, (root.contentWidth - width) / 2)
        y: Math.max(20, (root.contentHeight - height) / 2)
        width: pageImage.width
        height: pageImage.height
        color: "#FFFFFF"
        border.color: Theme.borderSubtle
        border.width: 1

        Image {
            id: pageImage
            width: {
                var geoms = pdfController.pageGeometries
                if (geoms && pdfController.currentPage < geoms.length) {
                    return geoms[pdfController.currentPage].width * pdfController.zoomLevel
                }
                return 612 * pdfController.zoomLevel
            }
            height: {
                var geoms = pdfController.pageGeometries
                if (geoms && pdfController.currentPage < geoms.length) {
                    return geoms[pdfController.currentPage].height * pdfController.zoomLevel
                }
                return 792 * pdfController.zoomLevel
            }
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            cache: false
            smooth: true
            mipmap: true
            source: pdfController.hasDocument ?
                ("image://pdf/" + pdfController.activeDocId + "/" + pdfController.currentPage +
                 "?zoom=" + pdfController.zoomLevel +
                 "&rot=" + pdfController.rotation +
                 "&v=" + pdfController.renderNonce) : ""
        }

        // Digital Signature Field Overlays
        Repeater {
            model: signatureController.getSignaturesForPage(pdfController.currentPage)

            Rectangle {
                id: sigOverlay
                x: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[0] * pageImage.width : 0
                y: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[1] * pageImage.height : 0
                width: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[2] * pageImage.width : 0
                height: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[3] * pageImage.height : 0
                visible: modelData.normRect && modelData.normRect.length === 4 && modelData.normRect[2] > 0
                color: sigMouse.containsMouse
                    ? (modelData.trustStatus === "trusted" ? "#154CAF50" : "#15FF9800")
                    : "transparent"
                border.color: modelData.trustStatus === "trusted" ? Theme.statusSuccess : Theme.statusWarning
                border.width: sigMouse.containsMouse ? 2 : 1
                radius: 3

                // Corner Status Badge
                Rectangle {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 2
                    height: 18
                    width: sigBadgeText.implicitWidth + 10
                    radius: 9
                    color: modelData.trustStatus === "trusted" ? Theme.statusSuccess : Theme.statusWarning
                    visible: sigOverlay.width > 60 && sigOverlay.height > 24

                    Row {
                        anchors.centerIn: parent
                        spacing: 2
                        Text {
                            text: modelData.trustStatus === "trusted" ? "✓" : "?"
                            font.pixelSize: 10
                            font.bold: true
                            color: "#FFFFFF"
                        }
                        Text {
                            id: sigBadgeText
                            text: modelData.trustStatus === "trusted" ? "Valid" : "Not Verified"
                            font.pixelSize: 9
                            font.bold: true
                            color: "#FFFFFF"
                        }
                    }
                }

                MouseArea {
                    id: sigMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        certDetailsDialogLoader.openCertificateDialog(index)
                    }
                }
            }
        }
    }
}
