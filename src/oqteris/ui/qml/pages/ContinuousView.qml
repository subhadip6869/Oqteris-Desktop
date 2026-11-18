import QtQuick
import QtQuick.Controls
import "../themes"

ListView {
    id: root
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    spacing: 16

    // -----------------------------------------------------------------------
    // Memory optimisation: delegate recycling
    // -----------------------------------------------------------------------
    // cacheBuffer controls how many *extra* pixels above/below the viewport Qt
    // pre-instantiates delegates in.  Setting it to 0 means only the delegates
    // that are actually visible are alive at any time, so a 500-page PDF never
    // has more than ~3–5 Image elements in memory simultaneously.
    // reuseItems: true lets Qt recycle delegate instances instead of destroying
    // and re-creating them, keeping delegate churn low while still releasing
    // the QImage references held by off-screen Image elements.
    cacheBuffer: 0
    reuseItems: true

    model: pdfController.pageCount

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

    // Track visible page index while scrolling
    onContentYChanged: {
        var idx = indexAt(contentX + width / 2, contentY + 100)
        if (idx >= 0 && idx < pdfController.pageCount && pdfController.currentPage !== idx) {
            pdfController.currentPage = idx
        }
    }

    Connections {
        target: pdfController
        function onCurrentPageChanged() {
            // When navigating externally (e.g. from thumbnail or search)
            if (!root.moving && !root.dragging) {
                root.positionViewAtIndex(pdfController.currentPage, ListView.Beginning)
            }
        }
    }

    delegate: Item {
        id: pageDelegate
        width: root.width
        height: pageImage.height + 20

        // Page paper sheet
        Rectangle {
            id: paperSheet
            anchors.centerIn: parent
            width: pageImage.width
            height: pageImage.height
            color: "#FFFFFF"
            border.color: Theme.borderSubtle
            border.width: 1

            Image {
                id: pageImage
                anchors.centerIn: parent
                // Scale width and height by current zoom level
                width: {
                    var geoms = pdfController.pageGeometries
                    if (geoms && index < geoms.length) {
                        return geoms[index].width * pdfController.zoomLevel
                    }
                    return 612 * pdfController.zoomLevel
                }
                height: {
                    var geoms = pdfController.pageGeometries
                    if (geoms && index < geoms.length) {
                        return geoms[index].height * pdfController.zoomLevel
                    }
                    return 792 * pdfController.zoomLevel
                }
                fillMode: Image.PreserveAspectFit
                asynchronous: true
                cache: false
                smooth: true
                mipmap: true
                source: pdfController.hasDocument ?
                    ("image://pdf/" + pdfController.activeDocId + "/" + index +
                     "?zoom=" + pdfController.zoomLevel +
                     "&rot=" + pdfController.rotation +
                     "&v=" + pdfController.renderNonce) : ""
            }

            // Digital Signature Field Overlays
            Repeater {
                model: signatureController.signaturesRevision >= 0
                    ? signatureController.getSignaturesForPage(index)
                    : []

                Rectangle {
                    id: sigOverlayCont
                    x: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[0] * pageImage.width : 0
                    y: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[1] * pageImage.height : 0
                    width: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[2] * pageImage.width : 0
                    height: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[3] * pageImage.height : 0
                    visible: modelData.normRect && modelData.normRect.length === 4 && modelData.normRect[2] > 0
                    color: "transparent"
                    border.color: sigContMouse.containsMouse ? Theme.brandPrimary : "transparent"
                    border.width: sigContMouse.containsMouse ? 1.5 : 0
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
                        id: sigContMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            mainPanelState.showLeftPanel = true
                            mainPanelState.currentPanelTab = "signatures"
                            certDetailsDialogLoader.openCertificateDialog(modelData.sigIndex !== undefined ? modelData.sigIndex : index)
                        }

                        ToolTip.visible: sigContMouse.containsMouse
                        ToolTip.delay: 300
                        ToolTip.text: {
                            var st = modelData.trustStatus === "trusted" ? "Digitally Signed & Trusted" : (modelData.trustStatus === "untrusted" ? "Valid (Untrusted Root CA)" : "Signature Invalid / Modified")
                            return "Digitally signed by " + modelData.signerName + "\nStatus: " + st + "\nClick to view certificate details."
                        }
                    }
                }
            }

            // Interactive markup canvas overlay
            Canvas {
                id: markupCanvas
                anchors.fill: pageImage
                visible: ribbonController.activeTool === "ink"

                property var currentStroke: []

                onPaint: {
                    var ctx = getContext("2d")
                    ctx.strokeStyle = "#000000"
                    ctx.lineWidth = 2 * pdfController.zoomLevel
                    ctx.lineCap = "round"
                    ctx.lineJoin = "round"

                    if (currentStroke.length >= 2) {
                        ctx.beginPath()
                        ctx.moveTo(currentStroke[0].x, currentStroke[0].y)
                        for (var i = 1; i < currentStroke.length; i++) {
                            ctx.lineTo(currentStroke[i].x, currentStroke[i].y)
                        }
                        ctx.stroke()
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    enabled: ribbonController.activeTool === "ink"
                    cursorShape: Qt.CrossCursor

                    onPressed: (mouse) => {
                        markupCanvas.currentStroke = [{ x: mouse.x, y: mouse.y }]
                        markupCanvas.requestPaint()
                    }

                    onPositionChanged: (mouse) => {
                        markupCanvas.currentStroke.push({ x: mouse.x, y: mouse.y })
                        markupCanvas.requestPaint()
                    }

                    onReleased: {
                        if (markupCanvas.currentStroke.length >= 2) {
                            // Normalize stroke coordinates back to PDF points
                            var normStroke = []
                            for (var i = 0; i < markupCanvas.currentStroke.length; i++) {
                                normStroke.push([
                                    markupCanvas.currentStroke[i].x / pdfController.zoomLevel,
                                    markupCanvas.currentStroke[i].y / pdfController.zoomLevel
                                ])
                            }
                            annotationController.addInkDrawing(index, [normStroke], "#000000", 2.0)
                        }
                        markupCanvas.currentStroke = []
                        markupCanvas.requestPaint()
                    }
                }
            }

            // Text Placement / Sticky Note placement mouse area
            MouseArea {
                anchors.fill: pageImage
                enabled: ribbonController.activeTool === "note" || ribbonController.activeTool === "stamp_approved"
                cursorShape: Qt.CrossCursor

                onClicked: (mouse) => {
                    var pdfX = mouse.x / pdfController.zoomLevel
                    var pdfY = mouse.y / pdfController.zoomLevel

                    if (ribbonController.activeTool === "note") {
                        annotationController.addStickyNote(index, pdfX, pdfY, "Comment Note", appController.developerName)
                        ribbonController.selectTool("select")
                    } else if (ribbonController.activeTool === "stamp_approved") {
                        var rect = [pdfX - 60, pdfY - 20, pdfX + 60, pdfY + 20]
                        annotationController.addStamp(index, rect, "APPROVED")
                        ribbonController.selectTool("select")
                    }
                }
            }
        }
    }
}
