import QtQuick
import QtQuick.Controls.Basic
import "../themes"

ListView {
    id: root
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    spacing: 16

    model: pdfController.pageCount

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
                model: signatureController.getSignaturesForPage(index)

                Rectangle {
                    id: sigOverlayCont
                    x: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[0] * pageImage.width : 0
                    y: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[1] * pageImage.height : 0
                    width: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[2] * pageImage.width : 0
                    height: (modelData.normRect && modelData.normRect.length === 4) ? modelData.normRect[3] * pageImage.height : 0
                    visible: modelData.normRect && modelData.normRect.length === 4 && modelData.normRect[2] > 0
                    color: sigContMouse.containsMouse
                        ? (modelData.trustStatus === "trusted" ? "#154CAF50" : "#15FF9800")
                        : "transparent"
                    border.color: modelData.trustStatus === "trusted" ? Theme.statusSuccess : Theme.statusWarning
                    border.width: sigContMouse.containsMouse ? 2 : 1
                    radius: 3

                    // Corner Status Badge
                    Rectangle {
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.margins: 2
                        height: 18
                        width: sigContBadgeText.implicitWidth + 10
                        radius: 9
                        color: modelData.trustStatus === "trusted" ? Theme.statusSuccess : Theme.statusWarning
                        visible: sigOverlayCont.width > 60 && sigOverlayCont.height > 24

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
                                id: sigContBadgeText
                                text: modelData.trustStatus === "trusted" ? "Valid" : "Not Verified"
                                font.pixelSize: 9
                                font.bold: true
                                color: "#FFFFFF"
                            }
                        }
                    }

                    MouseArea {
                        id: sigContMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            certDetailsDialogLoader.openCertificateDialog(index)
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
