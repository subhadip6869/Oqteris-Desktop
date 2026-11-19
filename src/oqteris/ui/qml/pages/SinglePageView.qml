import QtQuick
import QtQuick.Controls
import "../themes"

Flickable {
    id: root
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    contentWidth: Math.max(width, paperSheet.width + 40)
    contentHeight: Math.max(height, paperSheet.height + 40)

    // Ctrl + Mouse Wheel Zoom
    WheelHandler {
        id: wheelHandler
        acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
        acceptedModifiers: Qt.ControlModifier
        onWheel: (event) => {
            if (event.angleDelta.y > 0) {
                pdfController.zoomIn()
            } else if (event.angleDelta.y < 0) {
                pdfController.zoomOut()
            }
        }
    }

    ScrollBar.vertical: ScrollBar {
        id: vScrollBar
        policy: ScrollBar.AsNeeded
        width: 12
        z: 50
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
        z: 50
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

    // -----------------------------------------------------------------------
    // Hand Tool: Viewport Pan Drag Area
    // -----------------------------------------------------------------------
    MouseArea {
        id: handPanArea
        parent: root
        anchors.fill: root
        z: 40
        enabled: ribbonController.activeTool === "hand"
        visible: enabled
        hoverEnabled: true
        cursorShape: pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor

        property real startMouseX: 0
        property real startMouseY: 0
        property real startContentX: 0
        property real startContentY: 0

        onPressed: (mouse) => {
            startMouseX = mouse.x
            startMouseY = mouse.y
            startContentX = root.contentX
            startContentY = root.contentY
        }

        onPositionChanged: (mouse) => {
            if (pressed) {
                var dx = mouse.x - startMouseX
                var dy = mouse.y - startMouseY
                var maxX = Math.max(0, root.contentWidth - root.width)
                var maxY = Math.max(0, root.contentHeight - root.height)
                root.contentX = Math.max(0, Math.min(maxX, startContentX - dx))
                root.contentY = Math.max(0, Math.min(maxY, startContentY - dy))
            }
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

        // -------------------------------------------------------------------
        // Line-by-Line Text Selection Highlights
        // -------------------------------------------------------------------
        Repeater {
            model: (pdfController.selectionPageIndex === pdfController.currentPage) ? pdfController.selectionRects : []

            Rectangle {
                z: 25
                x: modelData.x0 * pdfController.zoomLevel
                y: modelData.y0 * pdfController.zoomLevel
                width: Math.max(2, (modelData.x1 - modelData.x0) * pdfController.zoomLevel)
                height: Math.max(2, (modelData.y1 - modelData.y0) * pdfController.zoomLevel)
                color: Theme.brandPrimary
                opacity: 0.30
                radius: 2
            }
        }

        // -------------------------------------------------------------------
        // Select Tool: Line-by-Line Text Selection MouseArea
        // -------------------------------------------------------------------
        MouseArea {
            id: selectMouseArea
            anchors.fill: pageImage
            z: 30
            enabled: ribbonController.activeTool === "select"
            visible: enabled
            hoverEnabled: true
            cursorShape: Qt.IBeamCursor

            property real pressX: 0
            property real pressY: 0
            property bool isDragging: false

            onPressed: (mouse) => {
                pressX = mouse.x
                pressY = mouse.y
                isDragging = false
                var zoom = pdfController.zoomLevel
                pdfController.updateSelection(pdfController.currentPage, pressX / zoom, pressY / zoom, pressX / zoom, pressY / zoom)
            }

            onPositionChanged: (mouse) => {
                if (pressed) {
                    isDragging = true
                    var zoom = pdfController.zoomLevel
                    pdfController.updateSelection(pdfController.currentPage, pressX / zoom, pressY / zoom, mouse.x / zoom, mouse.y / zoom)
                }
            }

            onReleased: (mouse) => {
                if (!isDragging || (Math.abs(mouse.x - pressX) < 4 && Math.abs(mouse.y - pressY) < 4)) {
                    pdfController.clearSelection()
                }
                isDragging = false
            }
        }

        // -------------------------------------------------------------------
        // Non-Text Objects Overlay (Images & Vector Shapes)
        // -------------------------------------------------------------------
        Repeater {
            model: (ribbonController.activeTool === "select") ? pdfController.getPageObjects(pdfController.currentPage) : []

            Item {
                z: 32
                x: modelData.x0 * pdfController.zoomLevel
                y: modelData.y0 * pdfController.zoomLevel
                width: Math.max(8, (modelData.x1 - modelData.x0) * pdfController.zoomLevel)
                height: Math.max(8, (modelData.y1 - modelData.y0) * pdfController.zoomLevel)

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor

                    onClicked: (mouse) => {
                        pdfController.selectObject(pdfController.currentPage, modelData)
                    }
                }
            }
        }

        // -------------------------------------------------------------------
        // Selected Object Box with 8 Foxit/Adobe Control Handles
        // -------------------------------------------------------------------
        Rectangle {
            id: selectedObjBox
            visible: pdfController.hasSelectedObject && pdfController.selectedObject.pageIndex === pdfController.currentPage
            z: 34
            x: ((pdfController.selectedObject && pdfController.selectedObject.x0) || 0) * pdfController.zoomLevel
            y: ((pdfController.selectedObject && pdfController.selectedObject.y0) || 0) * pdfController.zoomLevel
            width: Math.max(8, (((pdfController.selectedObject && pdfController.selectedObject.x1) || 0) - ((pdfController.selectedObject && pdfController.selectedObject.x0) || 0)) * pdfController.zoomLevel)
            height: Math.max(8, (((pdfController.selectedObject && pdfController.selectedObject.y1) || 0) - ((pdfController.selectedObject && pdfController.selectedObject.y0) || 0)) * pdfController.zoomLevel)
            color: Theme.brandPrimary
            opacity: 0.15
            border.color: Theme.brandPrimary
            border.width: 1.5

            // 8 Control Handles: corners and edge midpoints
            Repeater {
                model: [
                    { rx: 0, ry: 0 },
                    { rx: 0.5, ry: 0 },
                    { rx: 1.0, ry: 0 },
                    { rx: 0, ry: 0.5 },
                    { rx: 1.0, ry: 0.5 },
                    { rx: 0, ry: 1.0 },
                    { rx: 0.5, ry: 1.0 },
                    { rx: 1.0, ry: 1.0 }
                ]

                Rectangle {
                    width: 7
                    height: 7
                    x: parent.width * modelData.rx - width / 2
                    y: parent.height * modelData.ry - height / 2
                    color: "#FFFFFF"
                    border.color: Theme.brandPrimary
                    border.width: 1.5
                    radius: 1
                }
            }
        }

        // Digital Signature Field Overlays
        Repeater {
            model: (signatureController.signaturesRevision >= 0 && pdfController.currentPage >= 0)
                ? signatureController.getSignaturesForPage(pdfController.currentPage)
                : []

            Rectangle {
                id: sigOverlay
                z: 35
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

        // Interactive markup canvas overlay (Ink)
        Canvas {
            id: markupCanvas
            anchors.fill: pageImage
            z: 22
            visible: ribbonController.activeTool === "ink"
            enabled: ribbonController.activeTool === "ink"

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
                visible: enabled
                hoverEnabled: true
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
                        var normStroke = []
                        for (var i = 0; i < markupCanvas.currentStroke.length; i++) {
                            normStroke.push([
                                markupCanvas.currentStroke[i].x / pdfController.zoomLevel,
                                markupCanvas.currentStroke[i].y / pdfController.zoomLevel
                            ])
                        }
                        annotationController.addInkDrawing(pdfController.currentPage, [normStroke], "#000000", 2.0)
                    }
                    markupCanvas.currentStroke = []
                    markupCanvas.requestPaint()
                }
            }
        }

        // Text Placement / Sticky Note / Stamp placement mouse area
        MouseArea {
            anchors.fill: pageImage
            z: 21
            enabled: ribbonController.activeTool === "note" ||
                     ribbonController.activeTool === "stamp_approved" ||
                     ribbonController.activeTool === "stamp_confidential"
            visible: enabled
            hoverEnabled: true
            cursorShape: Qt.CrossCursor

            onClicked: (mouse) => {
                var pdfX = mouse.x / pdfController.zoomLevel
                var pdfY = mouse.y / pdfController.zoomLevel

                if (ribbonController.activeTool === "note") {
                    annotationController.addStickyNote(pdfController.currentPage, pdfX, pdfY, "Comment Note", appController.developerName)
                    ribbonController.selectTool("select")
                } else if (ribbonController.activeTool === "stamp_approved") {
                    var rectA = [pdfX - 60, pdfY - 20, pdfX + 60, pdfY + 20]
                    annotationController.addStamp(pdfController.currentPage, rectA, "APPROVED")
                    ribbonController.selectTool("select")
                } else if (ribbonController.activeTool === "stamp_confidential") {
                    var rectC = [pdfX - 70, pdfY - 20, pdfX + 70, pdfY + 20]
                    annotationController.addStamp(pdfController.currentPage, rectC, "CONFIDENTIAL")
                    ribbonController.selectTool("select")
                }
            }
        }
    }
}
