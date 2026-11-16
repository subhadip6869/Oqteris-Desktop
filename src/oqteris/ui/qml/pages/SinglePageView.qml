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
            model: (signatureController.signaturesRevision >= 0 && pdfController.currentPage >= 0)
                ? signatureController.getSignaturesForPage(pdfController.currentPage)
                : []

            Rectangle {
                id: sigOverlay
                x: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[0] * pageImage.width : 0
                y: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[1] * pageImage.height : 0
                width: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[2] * pageImage.width : 0
                height: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[3] * pageImage.height : 0
                visible: modelData.normRect && modelData.normRect.length === 4 && modelData.normRect[2] > 0
                color: modelData.trustStatus === "trusted"
                    ? "#FFFFFF"
                    : (sigMouse.containsMouse ? "#15FF9800" : "transparent")
                border.color: modelData.trustStatus === "trusted"
                    ? Theme.statusSuccess
                    : (modelData.trustStatus === "invalid" ? Theme.statusError : Theme.statusWarning)
                border.width: sigMouse.containsMouse ? 2 : 1
                radius: 2
                clip: true

                // When Trusted: Native Valid Signature Box Representation
                Item {
                    anchors.fill: parent
                    visible: modelData.trustStatus === "trusted"

                    // Left Details Column
                    Column {
                        anchors.left: parent.left
                        anchors.leftMargin: 4
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 1

                        Text {
                            text: "Signature valid"
                            font.pixelSize: Math.max(8, Math.min(13, sigOverlay.height * 0.19))
                            font.weight: Font.DemiBold
                            color: "#111111"
                        }
                        Text {
                            text: "Digitally Signed."
                            font.pixelSize: Math.max(7, Math.min(10, sigOverlay.height * 0.14))
                            color: "#222222"
                        }
                        Text {
                            text: "Name: " + (modelData.signerName || "Unknown")
                            font.pixelSize: Math.max(7, Math.min(10, sigOverlay.height * 0.14))
                            color: "#222222"
                        }
                        Text {
                            text: "Date: " + (modelData.signingTime || "")
                            font.pixelSize: Math.max(7, Math.min(10, sigOverlay.height * 0.14))
                            color: "#222222"
                            visible: modelData.signingTime !== ""
                        }
                        Text {
                            text: "Reason: " + (modelData.reason || "")
                            font.pixelSize: Math.max(7, Math.min(10, sigOverlay.height * 0.14))
                            color: "#222222"
                            visible: modelData.reason !== ""
                        }
                        Text {
                            text: "Location: " + (modelData.location || "")
                            font.pixelSize: Math.max(7, Math.min(10, sigOverlay.height * 0.14))
                            color: "#222222"
                            visible: modelData.location !== ""
                        }
                    }

                    // Bold Green Checkmark with 3D Shadow
                    Item {
                        anchors.right: parent.right
                        anchors.rightMargin: parent.width * 0.12
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.height * 0.8
                        height: parent.height * 0.8

                        Text {
                            anchors.centerIn: parent
                            anchors.horizontalCenterOffset: 2
                            anchors.verticalCenterOffset: 2
                            text: "✔"
                            font.pixelSize: Math.max(16, Math.min(parent.height * 1.1, 48))
                            font.bold: true
                            color: "#222222"
                            rotation: -4
                        }
                        Text {
                            anchors.centerIn: parent
                            text: "✔"
                            font.pixelSize: Math.max(16, Math.min(parent.height * 1.1, 48))
                            font.bold: true
                            color: "#00A843"
                            rotation: -4
                        }
                    }
                }

                // Corner Status Badge (when untrusted or invalid)
                Rectangle {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 2
                    height: 18
                    width: sigBadgeText.implicitWidth + 10
                    radius: 9
                    color: modelData.trustStatus === "invalid" ? Theme.statusError : Theme.statusWarning
                    visible: modelData.trustStatus !== "trusted" && sigOverlay.width > 60 && sigOverlay.height > 24

                    Row {
                        anchors.centerIn: parent
                        spacing: 2
                        Text {
                            text: modelData.trustStatus === "invalid" ? "✕" : "?"
                            font.pixelSize: 10
                            font.bold: true
                            color: "#FFFFFF"
                        }
                        Text {
                            id: sigBadgeText
                            text: modelData.trustStatus === "invalid" ? "Invalid" : "Not Verified"
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
                        certDetailsDialogLoader.openCertificateDialog(modelData.sigIndex !== undefined ? modelData.sigIndex : index)
                    }

                    ToolTip.visible: sigMouse.containsMouse
                    ToolTip.delay: 400
                    ToolTip.text: modelData.trustStatus === "trusted"
                        ? ("Digitally signed by " + modelData.signerName + "\nSignature is VALID and certificate is TRUSTED.\nClick to view certificate details.")
                        : ("Digitally signed by " + modelData.signerName + "\nSignature is NOT VERIFIED.\nClick to view details or trust certificate.")
                }
            }
        }
    }
}
