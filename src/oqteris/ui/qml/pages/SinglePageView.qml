import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Flickable {
    id: root
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    contentWidth: Math.max(width, paperSheet.width + 40)
    contentHeight: Math.max(height, paperSheet.height + 40)

    ScrollBar.vertical: ScrollBar {
        id: vScrollBar
        policy: ScrollBar.AsNeeded
        width: 12
        z: 10
        visible: vScrollBar.size < 1.0

        contentItem: Rectangle {
            implicitWidth: 8
            implicitHeight: 30
            radius: 4
            color: vScrollBar.pressed
                ? Theme.brandPrimary
                : (vScrollBar.hovered
                    ? (appController.isDarkMode ? "#8E8E93" : "#767676")
                    : (appController.isDarkMode ? "#5A5A5E" : "#B5B5B5"))
        }

        background: Rectangle {
            implicitWidth: 12
            color: vScrollBar.hovered
                ? (appController.isDarkMode ? "#252526" : "#E8E8E8")
                : "transparent"
        }
    }

    ScrollBar.horizontal: ScrollBar {
        id: hScrollBar
        policy: ScrollBar.AsNeeded
        height: 12
        z: 10
        visible: hScrollBar.size < 1.0

        contentItem: Rectangle {
            implicitWidth: 30
            implicitHeight: 8
            radius: 4
            color: hScrollBar.pressed
                ? Theme.brandPrimary
                : (hScrollBar.hovered
                    ? (appController.isDarkMode ? "#8E8E93" : "#767676")
                    : (appController.isDarkMode ? "#5A5A5E" : "#B5B5B5"))
        }

        background: Rectangle {
            implicitHeight: 12
            color: hScrollBar.hovered
                ? (appController.isDarkMode ? "#252526" : "#E8E8E8")
                : "transparent"
        }
    }

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
                color: "transparent"
                border.color: sigMouse.containsMouse ? Theme.brandPrimary : "transparent"
                border.width: sigMouse.containsMouse ? 1.5 : 0
                radius: 2

                // For non-layered signatures only: round badge in top-left corner
                Rectangle {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.margins: 2
                    height: 18
                    width: 18
                    radius: 9
                    color: {
                        if (modelData.trustStatus === "trusted") return Theme.statusSuccess
                        if (modelData.trustStatus === "untrusted") return Theme.statusWarning
                        return Theme.statusError
                    }
                    visible: !modelData.isLayered

                    Text {
                        anchors.centerIn: parent
                        text: {
                            if (modelData.trustStatus === "trusted") return "✓"
                            if (modelData.trustStatus === "untrusted") return "?"
                            return "✕"
                        }
                        font.pixelSize: 10
                        font.bold: true
                        color: "#FFFFFF"
                    }
                }

                MouseArea {
                    id: sigMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        mainPanelState.showLeftPanel = true
                        mainPanelState.currentPanelTab = "signatures"
                        certDetailsDialogLoader.openCertificateDialog(modelData.sigIndex !== undefined ? modelData.sigIndex : index)
                    }

                    ToolTip.visible: sigMouse.containsMouse
                    ToolTip.delay: 300
                    ToolTip.text: {
                        var st = modelData.trustStatus === "trusted" ? "Digitally Signed & Trusted" : (modelData.trustStatus === "untrusted" ? "Valid (Untrusted Root CA)" : "Signature Invalid / Modified")
                        return "Digitally signed by " + modelData.signerName + "\nStatus: " + st + "\nClick to view certificate details."
                    }
                }
            }
        }
    }
}
