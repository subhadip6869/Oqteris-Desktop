import QtQuick
import QtQuick.Controls
import "../themes"

ListView {
    id: root
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    spacing: 16

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

    // -----------------------------------------------------------------------
    // Memory & rendering optimisation: buffer 1200px (1-2 pages)
    // -----------------------------------------------------------------------
    cacheBuffer: 1200
    reuseItems: true

    model: pdfController.pageCount

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

    // -----------------------------------------------------------------------
    // Hand Tool: Viewport Pan Drag Area
    // -----------------------------------------------------------------------
    MouseArea {
        id: contHandPanArea
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
                var maxY = Math.max(0, root.contentHeight - root.height)
                var maxX = Math.max(0, root.contentWidth - root.width)
                root.contentY = Math.max(0, Math.min(maxY, startContentY - dy))
                if (maxX > 0) {
                    root.contentX = Math.max(0, Math.min(maxX, startContentX - dx))
                }
            }
        }
    }

    // Track visible page index while scrolling
    property bool isInternalScroll: false

    onContentYChanged: {
        var idx = indexAt(contentX + width / 2, contentY + 100)
        if (idx >= 0 && idx < pdfController.pageCount && pdfController.currentPage !== idx) {
            isInternalScroll = true
            pdfController.currentPage = idx
            isInternalScroll = false
        }
    }

    Connections {
        target: pdfController
        function onCurrentPageChanged() {
            // Only reposition when navigating externally (e.g. from thumbnail or search)
            if (!root.isInternalScroll && !root.moving && !root.dragging) {
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

            // ---------------------------------------------------------------
            // Line-by-Line Text Selection Highlights
            // ---------------------------------------------------------------
            Repeater {
                model: (pdfController.selectionPageIndex === index) ? pdfController.selectionRects : []

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

            // ---------------------------------------------------------------
            // Select Tool: Line-by-Line Text Selection MouseArea
            // ---------------------------------------------------------------
            MouseArea {
                id: contSelectMouseArea
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
                    pdfController.currentPage = index
                    var zoom = pdfController.zoomLevel
                    pdfController.updateSelection(index, pressX / zoom, pressY / zoom, pressX / zoom, pressY / zoom)
                }

                onPositionChanged: (mouse) => {
                    if (pressed) {
                        isDragging = true
                        var zoom = pdfController.zoomLevel
                        pdfController.updateSelection(index, pressX / zoom, pressY / zoom, mouse.x / zoom, mouse.y / zoom)
                    }
                }

                onReleased: (mouse) => {
                    if (!isDragging || (Math.abs(mouse.x - pressX) < 4 && Math.abs(mouse.y - pressY) < 4)) {
                        pdfController.clearSelection()
                    }
                    isDragging = false
                }
            }

            // ---------------------------------------------------------------
            // Non-Text Objects Overlay (Images & Vector Shapes)
            // ---------------------------------------------------------------
            Repeater {
                model: (ribbonController.activeTool === "select") ? pdfController.getPageObjects(index) : []

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
                            pdfController.selectObject(index, modelData)
                        }
                    }
                }
            }

            // ---------------------------------------------------------------
            // Selected Object Box with 8 Foxit/Adobe Control Handles
            // ---------------------------------------------------------------
            Rectangle {
                id: selectedObjBox
                visible: pdfController.hasSelectedObject && pdfController.selectedObject.pageIndex === index
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
                model: signatureController.signaturesRevision >= 0
                    ? signatureController.getSignaturesForPage(index)
                    : []

                Rectangle {
                    id: sigOverlayCont
                    z: 35
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
                            annotationController.addInkDrawing(index, [normStroke], "#000000", 2.0)
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
                        annotationController.addStickyNote(index, pdfX, pdfY, "Comment Note", appController.developerName)
                        ribbonController.selectTool("select")
                    } else if (ribbonController.activeTool === "stamp_approved") {
                        var rectA = [pdfX - 60, pdfY - 20, pdfX + 60, pdfY + 20]
                        annotationController.addStamp(index, rectA, "APPROVED")
                        ribbonController.selectTool("select")
                    } else if (ribbonController.activeTool === "stamp_confidential") {
                        var rectC = [pdfX - 70, pdfY - 20, pdfX + 70, pdfY + 20]
                        annotationController.addStamp(index, rectC, "CONFIDENTIAL")
                        ribbonController.selectTool("select")
                    }
                }
            }
        }
    }
}
