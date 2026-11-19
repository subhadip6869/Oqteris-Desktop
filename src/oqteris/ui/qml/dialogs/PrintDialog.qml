import QtQuick
import QtQuick.Controls
import "../components"
import "../themes"

Dialog {
    id: root
    width: 800
    height: 580
    modal: true
    anchors.centerIn: parent

    background: Rectangle {
        color: Theme.cardBackground
        border.color: Theme.borderSubtle
        border.width: 1
        radius: 6
    }

    // ── State ──────────────────────────────────────────────────────────────
    property var printerList: []
    property int previewPage: 0          // 0-based index of preview sheet
    property var printPageList: []        // resolved list of 0-based page indices

    property int copiesCount: 1
    property int customScaleValue: 100

    readonly property int nupCount: bookletCheck.checked ? 2 : ([1, 2, 4, 6, 9][pagesPerSheetCombo.currentIndex] || 1)
    readonly property int totalSheets: Math.max(1, Math.ceil(printPageList.length / nupCount))
    readonly property int currentSheet: Math.max(0, Math.min(previewPage, totalSheets - 1))

    readonly property int gridCols: {
        if (nupCount === 1) return 1
        if (nupCount === 2) return (previewContainer.paperAspect >= 1.0) ? 2 : 1
        if (nupCount === 4) return 2
        if (nupCount === 6) return (previewContainer.paperAspect >= 1.0) ? 3 : 2
        if (nupCount === 9) return 3
        return 1
    }
    readonly property int gridRows: {
        if (nupCount === 1) return 1
        if (nupCount === 2) return (previewContainer.paperAspect >= 1.0) ? 1 : 2
        if (nupCount === 4) return 2
        if (nupCount === 6) return (previewContainer.paperAspect >= 1.0) ? 2 : 3
        if (nupCount === 9) return 3
        return 1
    }

    // ── Public API ─────────────────────────────────────────────────────────
    onAboutToShow: {
        _populate()
    }

    onClosed: {
        printPageList = []
        previewPage = 0
        pdfController.clearPrintPreviewCache()
    }

    function openForDocument() {
        open()
    }

    function _populate() {
        var printers = pdfController.getAvailablePrinters()
        printerList = printers
        printerCombo.model = printers
        // select default printer
        var def = pdfController.getDefaultPrinter()
        var idx = printers.indexOf(def)
        printerCombo.currentIndex = idx >= 0 ? idx : 0
        // resolve initial page list
        previewPage = 0
        _resolvePageList()
    }

    function _resolvePageList() {
        var range = "all"
        if (rangeCurrentPage.checked) range = "current"
        else if (rangeCustom.checked) range = customRangeInput.text

        var totalPages = pdfController.pageCount
        var pages = []
        if (range === "all") {
            for (var i = 0; i < totalPages; i++) pages.push(i)
        } else if (range === "current") {
            pages = [pdfController.currentPage]
        } else {
            pages = pdfController.parsePageRange(range, totalPages)
        }
        if (reverseCheck.checked) pages = pages.slice().reverse()

        // Saddle-stitch booklet reordering
        if (bookletCheck.checked && pages.length > 0) {
            var padded = pages.slice()
            while (padded.length % 4 !== 0) {
                padded.push(-1)
            }
            var nSheets = Math.floor(padded.length / 2)
            var reordered = []
            var lo = 0, hi = padded.length - 1
            for (var s = 0; s < Math.floor(nSheets / 2) + (nSheets % 2); s++) {
                reordered.push(padded[hi])
                reordered.push(padded[lo])
                lo++
                hi--
                if (lo <= hi) {
                    reordered.push(padded[lo])
                    reordered.push(padded[hi])
                    lo++
                    hi--
                }
            }
            pages = reordered
        }

        printPageList = pages
        if (previewPage >= totalSheets) previewPage = Math.max(0, totalSheets - 1)
    }

    function _buildSettings() {
        var range = "all"
        if (rangeCurrentPage.checked) range = "current"
        else if (rangeCustom.checked) range = customRangeInput.text

        var scale = "fit"
        if (scaleActual.checked) scale = "actual"
        else if (scaleCustom.checked) scale = "custom"

        var orient = "auto"
        if (orientPortrait.checked) orient = "portrait"
        else if (orientLandscape.checked) orient = "landscape"

        var duplex = "none"
        if (duplexLong.checked) duplex = "long_edge"
        else if (duplexShort.checked) duplex = "short_edge"

        var nupVal = [1, 2, 4, 6, 9][pagesPerSheetCombo.currentIndex] || 1
        var orderMap = ["ltr", "rtl", "ttb"]

        return {
            "printerName":    printerCombo.currentText,
            "pageRange":      range,
            "copies":         copiesCount,
            "collate":        collateCheck.checked,
            "reverseOrder":   reverseCheck.checked,
            "scale":          scale,
            "scalePercent":   customScaleValue,
            "orientation":    orient,
            "nup":            nupVal,
            "nupOrder":       orderMap[pageOrderCombo.currentIndex] || "ltr",
            "booklet":        bookletCheck.checked,
            "duplex":         duplex,
            "grayscale":      grayscaleCheck.checked,
            "marginTop":      parseFloat(marginTopInput.text)    || 0,
            "marginBottom":   parseFloat(marginBottomInput.text) || 0,
            "marginLeft":     parseFloat(marginLeftInput.text)   || 0,
            "marginRight":    parseFloat(marginRightInput.text)  || 0
        }
    }

    // ── Root layout: header + body ─────────────────────────────────────────
    Column {
        anchors.fill: parent
        spacing: 0

        // ── Title Header ──────────────────────────────────────────────────
        Rectangle {
            width: parent.width
            height: 44
            color: Theme.panelBackground
            radius: 6

            // clip bottom corners square
            Rectangle {
                width: parent.width
                height: parent.height / 2
                anchors.bottom: parent.bottom
                color: parent.color
            }

            Item {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16

                Row {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 10

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "🖨"
                        font.pixelSize: 20
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Print"
                        font.pixelSize: Theme.fontSizeLarge
                        font.weight: Font.DemiBold
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }
                }

                // Close button (cross icon)
                Rectangle {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    width: 28
                    height: 28
                    radius: 4
                    color: closeArea.containsMouse ? Theme.buttonHover : "transparent"

                    OqIcon {
                        anchors.centerIn: parent
                        name: "close"
                        size: 14
                        color: closeArea.containsMouse ? Theme.textPrimary : Theme.textSecondary
                    }

                    MouseArea {
                        id: closeArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.close()
                    }
                }
            }

            // bottom divider
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        // ── Body: left settings + right preview ───────────────────────────
        Row {
            width: parent.width
            height: parent.height - 44 - 48   // minus header and footer

            // ── LEFT: Scrollable settings ─────────────────────────────────
            Rectangle {
                width: 360
                height: parent.height
                color: "transparent"

                ScrollView {
                    anchors.fill: parent
                    clip: true
                    contentWidth: availableWidth

                    Column {
                        width: 344
                        x: 8
                        topPadding: 12
                        bottomPadding: 12
                        spacing: 0

                        // ── SECTION: Printer ──────────────────────────────
                        SectionHeader { label: "PRINTER" }

                        Row {
                            width: parent.width
                            spacing: 6
                            padding: 0
                            topPadding: 6
                            bottomPadding: 8

                            ComboBox {
                                id: printerCombo
                                width: parent.width - 90
                                height: 28
                                font.pixelSize: Theme.fontSizeSmall
                                font.family: Theme.fontFamily

                                background: Rectangle {
                                    color: Theme.inputBackground
                                    border.color: printerCombo.activeFocus ? Theme.borderFocused : Theme.borderSubtle
                                    border.width: 1
                                    radius: 3
                                }
                                contentItem: Text {
                                    leftPadding: 6
                                    text: printerCombo.displayText
                                    font: printerCombo.font
                                    color: Theme.textPrimary
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                            }

                            OqButton {
                                text: "Properties..."
                                height: 28
                                width: 84
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: "Use system print settings"
                                property bool hovered: false
                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onEntered: parent.hovered = true
                                    onExited: parent.hovered = false
                                }
                            }
                        }

                        SectionDivider {}

                        // ── SECTION: Page Range ───────────────────────────
                        SectionHeader { label: "PAGE RANGE" }

                        Column {
                            width: parent.width
                            topPadding: 6
                            bottomPadding: 8
                            spacing: 6

                            OqRadioButton {
                                id: rangeAll
                                text: "All Pages"
                                checked: true
                                onClicked: { rangeCurrentPage.checked = false; rangeCustom.checked = false; root._resolvePageList() }
                            }

                            OqRadioButton {
                                id: rangeCurrentPage
                                text: "Current Page"
                                onClicked: { rangeAll.checked = false; rangeCustom.checked = false; root._resolvePageList() }
                            }

                            Row {
                                spacing: 8
                                OqRadioButton {
                                    id: rangeCustom
                                    text: "Custom Range:"
                                    onClicked: { rangeAll.checked = false; rangeCurrentPage.checked = false; root._resolvePageList() }
                                }
                                Rectangle {
                                    width: 120
                                    height: 24
                                    color: Theme.inputBackground
                                    border.color: rangeCustom.checked ? Theme.borderFocused : Theme.borderSubtle
                                    border.width: 1
                                    radius: 3
                                    opacity: rangeCustom.checked ? 1.0 : 0.5

                                    TextInput {
                                        id: customRangeInput
                                        anchors.fill: parent
                                        anchors.margins: 4
                                        font.pixelSize: Theme.fontSizeSmall
                                        font.family: Theme.fontFamily
                                        color: Theme.textPrimary
                                        enabled: rangeCustom.checked
                                        onTextChanged: if (rangeCustom.checked) root._resolvePageList()

                                        Text {
                                            anchors.fill: parent
                                            text: "e.g. 1,3,5-8"
                                            font: customRangeInput.font
                                            color: Theme.textSecondary
                                            visible: !customRangeInput.text && !customRangeInput.activeFocus
                                        }
                                    }
                                }
                            }
                        }

                        SectionDivider {}

                        // ── SECTION: Print Settings ───────────────────────
                        SectionHeader { label: "PRINT SETTINGS" }

                        Column {
                            width: parent.width
                            topPadding: 6
                            bottomPadding: 8
                            spacing: 8

                            Row {
                                spacing: 10
                                Text {
                                    text: "Copies:"
                                    anchors.verticalCenter: parent.verticalCenter
                                    font.pixelSize: Theme.fontSizeSmall
                                    font.family: Theme.fontFamily
                                    color: Theme.textPrimary
                                    width: 50
                                }

                                // Copies spin control
                                Row {
                                    spacing: 0
                                    Rectangle {
                                        width: 24; height: 26
                                        color: copiesDecBtn.containsMouse ? Theme.buttonHover : Theme.inputBackground
                                        border.color: Theme.borderSubtle; border.width: 1
                                        radius: 3
                                        Text { anchors.centerIn: parent; text: "−"; font.pixelSize: 14; color: Theme.textPrimary }
                                        MouseArea {
                                            id: copiesDecBtn
                                            anchors.fill: parent; hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: if (root.copiesCount > 1) root.copiesCount--
                                        }
                                    }
                                    Rectangle {
                                        width: 40; height: 26
                                        color: Theme.inputBackground
                                        border.color: Theme.borderSubtle; border.width: 1
                                        Text {
                                            anchors.centerIn: parent
                                            text: root.copiesCount
                                            font.pixelSize: Theme.fontSizeSmall
                                            font.family: Theme.fontFamily
                                            color: Theme.textPrimary
                                        }
                                    }
                                    Rectangle {
                                        width: 24; height: 26
                                        color: copiesIncBtn.containsMouse ? Theme.buttonHover : Theme.inputBackground
                                        border.color: Theme.borderSubtle; border.width: 1
                                        radius: 3
                                        Text { anchors.centerIn: parent; text: "+"; font.pixelSize: 14; color: Theme.textPrimary }
                                        MouseArea {
                                            id: copiesIncBtn
                                            anchors.fill: parent; hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: if (root.copiesCount < 999) root.copiesCount++
                                        }
                                    }
                                }
                            }

                            OqCheckBox { id: collateCheck; text: "Collate"; checked: true }
                            OqCheckBox {
                                id: reverseCheck; text: "Reverse Order"; checked: false
                                onToggled: root._resolvePageList()
                            }
                        }

                        SectionDivider {}

                        // ── SECTION: Page Scaling ─────────────────────────
                        SectionHeader { label: "PAGE SCALING" }

                        Column {
                            width: parent.width
                            topPadding: 6
                            bottomPadding: 8
                            spacing: 6

                            OqRadioButton {
                                id: scaleFit; text: "Fit to Printable Area"; checked: true
                                onClicked: { scaleActual.checked = false; scaleCustom.checked = false }
                            }
                            OqRadioButton {
                                id: scaleActual; text: "Actual Size"
                                onClicked: { scaleFit.checked = false; scaleCustom.checked = false }
                            }
                            Row {
                                spacing: 8
                                OqRadioButton {
                                    id: scaleCustom; text: "Custom Scale:"
                                    onClicked: { scaleFit.checked = false; scaleActual.checked = false }
                                }
                                // custom scale spin
                                Row {
                                    spacing: 0
                                    opacity: scaleCustom.checked ? 1.0 : 0.5
                                    Rectangle {
                                        width: 22; height: 22
                                        color: scaleDecBtn.containsMouse ? Theme.buttonHover : Theme.inputBackground
                                        border.color: Theme.borderSubtle; border.width: 1; radius: 3
                                        Text { anchors.centerIn: parent; text: "−"; font.pixelSize: 13; color: Theme.textPrimary }
                                        MouseArea {
                                            id: scaleDecBtn; anchors.fill: parent; hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor; enabled: scaleCustom.checked
                                            onClicked: if (root.customScaleValue > 10) root.customScaleValue -= 10
                                        }
                                    }
                                    Rectangle {
                                        width: 46; height: 22
                                        color: Theme.inputBackground
                                        border.color: Theme.borderSubtle; border.width: 1
                                        Text {
                                            anchors.centerIn: parent
                                            text: root.customScaleValue + "%"
                                            font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                            color: Theme.textPrimary
                                        }
                                    }
                                    Rectangle {
                                        width: 22; height: 22
                                        color: scaleIncBtn.containsMouse ? Theme.buttonHover : Theme.inputBackground
                                        border.color: Theme.borderSubtle; border.width: 1; radius: 3
                                        Text { anchors.centerIn: parent; text: "+"; font.pixelSize: 13; color: Theme.textPrimary }
                                        MouseArea {
                                            id: scaleIncBtn; anchors.fill: parent; hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor; enabled: scaleCustom.checked
                                            onClicked: if (root.customScaleValue < 200) root.customScaleValue += 10
                                        }
                                    }
                                }
                            }
                        }

                        SectionDivider {}

                        // ── SECTION: Orientation ──────────────────────────
                        SectionHeader { label: "ORIENTATION" }

                        Column {
                            width: parent.width
                            topPadding: 6
                            bottomPadding: 8
                            spacing: 6

                            OqRadioButton {
                                id: orientAuto; text: "Auto (match PDF)"; checked: true
                                onClicked: { orientPortrait.checked = false; orientLandscape.checked = false }
                            }
                            OqRadioButton {
                                id: orientPortrait; text: "Portrait"
                                onClicked: { orientAuto.checked = false; orientLandscape.checked = false }
                            }
                            OqRadioButton {
                                id: orientLandscape; text: "Landscape"
                                onClicked: { orientAuto.checked = false; orientPortrait.checked = false }
                            }
                        }

                        SectionDivider {}

                        // ── SECTION: Page Layout ──────────────────────────
                        SectionHeader { label: "PAGE LAYOUT" }

                        Column {
                            width: parent.width
                            topPadding: 6
                            bottomPadding: 8
                            spacing: 8

                            Row {
                                spacing: 10
                                Text {
                                    text: "Pages per Sheet:"
                                    anchors.verticalCenter: parent.verticalCenter
                                    font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                    color: Theme.textPrimary; width: 110
                                }
                                ComboBox {
                                    id: pagesPerSheetCombo
                                    model: ["1", "2", "4", "6", "9"]
                                    width: 70; height: 26
                                    enabled: !bookletCheck.checked
                                    font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                    onCurrentIndexChanged: { root.previewPage = 0; root._resolvePageList() }
                                    background: Rectangle {
                                        color: Theme.inputBackground
                                        border.color: Theme.borderSubtle; border.width: 1; radius: 3
                                        opacity: pagesPerSheetCombo.enabled ? 1.0 : 0.5
                                    }
                                    contentItem: Text {
                                        leftPadding: 6; text: pagesPerSheetCombo.displayText
                                        font: pagesPerSheetCombo.font; color: Theme.textPrimary
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                }
                            }

                            Row {
                                spacing: 10
                                opacity: (pagesPerSheetCombo.currentIndex > 0 && !bookletCheck.checked) ? 1.0 : 0.5
                                Text {
                                    text: "Page Order:"
                                    anchors.verticalCenter: parent.verticalCenter
                                    font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                    color: Theme.textPrimary; width: 110
                                }
                                ComboBox {
                                    id: pageOrderCombo
                                    model: ["Left to Right", "Right to Left", "Top to Bottom"]
                                    width: 140; height: 26
                                    enabled: pagesPerSheetCombo.currentIndex > 0 && !bookletCheck.checked
                                    font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                    background: Rectangle {
                                        color: Theme.inputBackground
                                        border.color: Theme.borderSubtle; border.width: 1; radius: 3
                                    }
                                    contentItem: Text {
                                        leftPadding: 6; text: pageOrderCombo.displayText
                                        font: pageOrderCombo.font; color: Theme.textPrimary
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                }
                            }

                            OqCheckBox {
                                id: bookletCheck; text: "Booklet"
                                onToggled: { root.previewPage = 0; root._resolvePageList() }
                            }

                            Text {
                                visible: bookletCheck.checked
                                text: "Prints 2 pages/sheet in saddle-stitch order"
                                font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                color: Theme.textSecondary
                                font.italic: true
                            }
                        }

                        SectionDivider {}

                        // ── SECTION: Duplex Printing ──────────────────────
                        SectionHeader { label: "DUPLEX PRINTING" }

                        Column {
                            width: parent.width
                            topPadding: 6
                            bottomPadding: 4
                            spacing: 6

                            OqRadioButton {
                                id: duplexNone; text: "Single-Sided"; checked: true
                                onClicked: { duplexLong.checked = false; duplexShort.checked = false }
                            }
                            OqRadioButton {
                                id: duplexLong; text: "Both Sides - Long Edge (Flip on Long)"
                                onClicked: { duplexNone.checked = false; duplexShort.checked = false }
                            }
                            OqRadioButton {
                                id: duplexShort; text: "Both Sides - Short Edge (Flip on Short)"
                                onClicked: { duplexNone.checked = false; duplexLong.checked = false }
                            }
                            Text {
                                text: "(Printer must support duplex)"
                                font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                color: Theme.textSecondary; font.italic: true
                            }
                        }

                        SectionDivider {}

                        // ── SECTION: Image & Color ────────────────────────
                        SectionHeader { label: "IMAGE & COLOR" }

                        Column {
                            width: parent.width
                            topPadding: 6
                            bottomPadding: 8
                            spacing: 6

                            OqCheckBox {
                                id: grayscaleCheck
                                text: "Grayscale (Black & White)"
                            }
                        }

                        SectionDivider {}

                        // ── SECTION: Margins ──────────────────────────────
                        SectionHeader { label: "MARGINS (mm)" }

                        Grid {
                            columns: 2
                            columnSpacing: 12
                            rowSpacing: 8
                            topPadding: 6
                            bottomPadding: 8

                            // Top
                            Row { spacing: 6
                                Text { text: "Top:"; width: 48; anchors.verticalCenter: parent.verticalCenter; font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily; color: Theme.textPrimary }
                                MarginInput { id: marginTopInput }
                            }
                            // Right
                            Row { spacing: 6
                                Text { text: "Right:"; width: 48; anchors.verticalCenter: parent.verticalCenter; font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily; color: Theme.textPrimary }
                                MarginInput { id: marginRightInput }
                            }
                            // Bottom
                            Row { spacing: 6
                                Text { text: "Bottom:"; width: 48; anchors.verticalCenter: parent.verticalCenter; font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily; color: Theme.textPrimary }
                                MarginInput { id: marginBottomInput }
                            }
                            // Left
                            Row { spacing: 6
                                Text { text: "Left:"; width: 48; anchors.verticalCenter: parent.verticalCenter; font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily; color: Theme.textPrimary }
                                MarginInput { id: marginLeftInput }
                            }
                        }

                        Item { width: 1; height: 8 }   // bottom padding
                    }  // Column (scroll content)
                }  // ScrollView
            }  // LEFT rectangle

            // ── Vertical divider between columns ─────────────────────────
            Rectangle { width: 1; height: parent.height; color: Theme.divider }

            // ── RIGHT: Print Preview ──────────────────────────────────────
            Rectangle {
                width: parent.width - 361
                height: parent.height
                color: Theme.workspaceBackground

                Column {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    // Info row: printer on left, orientation on right (properly bounded)
                    Item {
                        width: parent.width
                        height: 20

                        Text {
                            anchors.left: parent.left
                            anchors.right: orientInfoText.left
                            anchors.rightMargin: 8
                            anchors.verticalCenter: parent.verticalCenter
                            text: printerCombo.currentText
                            font.pixelSize: Theme.fontSizeSmall
                            font.family: Theme.fontFamily
                            color: Theme.textSecondary
                            elide: Text.ElideRight
                        }

                        Text {
                            id: orientInfoText
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            text: orientAuto.checked ? "Auto" : (orientPortrait.checked ? "⬛ Portrait" : "🖥 Landscape")
                            font.pixelSize: Theme.fontSizeSmall
                            font.family: Theme.fontFamily
                            color: Theme.textSecondary
                        }
                    }

                    // Page preview area
                    Item {
                        id: previewContainer
                        width: parent.width
                        height: parent.height - 68

                        // Determine paper aspect ratio based on orientation setting and page geometry
                        property real paperAspect: {
                            var geoms = pdfController.pageGeometries
                            var pIdx = (root.printPageList.length > 0) ? root.printPageList[Math.min(root.previewPage, root.printPageList.length - 1)] : 0
                            var pw = 595.0, ph = 842.0
                            if (geoms && geoms.length > pIdx && geoms[pIdx].width > 0 && geoms[pIdx].height > 0) {
                                pw = geoms[pIdx].width
                                ph = geoms[pIdx].height
                            }
                            if (orientLandscape.checked) {
                                return Math.max(pw, ph) / Math.min(pw, ph)
                            } else if (orientPortrait.checked) {
                                return Math.min(pw, ph) / Math.max(pw, ph)
                            } else {
                                return pw / ph
                            }
                        }

                        property real availW: Math.max(50, width - 24)
                        property real availH: Math.max(50, height - 24)
                        property real previewW: (availW / availH < paperAspect) ? availW : (availH * paperAspect)
                        property real previewH: previewW / paperAspect

                        // drop shadow
                        Rectangle {
                            anchors.centerIn: parent
                            width: pagePreview.width + 6
                            height: pagePreview.height + 6
                            color: Qt.rgba(0, 0, 0, 0.3)
                            radius: 3
                        }

                        // white paper sheet
                        Rectangle {
                            id: pagePreview
                            anchors.centerIn: parent
                            width: parent.previewW
                            height: parent.previewH
                            color: "#FFFFFF"
                            radius: 1
                            clip: true

                            // Fallback if no pages
                            Text {
                                anchors.centerIn: parent
                                text: pdfController.hasDocument ? "No pages selected" : "No document open"
                                font.pixelSize: Theme.fontSizeMedium
                                font.family: Theme.fontFamily
                                color: "#888888"
                                visible: root.printPageList.length === 0
                            }

                            // Printable area (with real-time margin visualization)
                            Rectangle {
                                id: printableArea
                                anchors.fill: parent
                                anchors.topMargin: Math.max(0, Math.min(parent.height * 0.25, (parseFloat(marginTopInput.text) || 0) * (parent.height / (previewContainer.paperAspect >= 1.0 ? 210.0 : 297.0))))
                                anchors.bottomMargin: Math.max(0, Math.min(parent.height * 0.25, (parseFloat(marginBottomInput.text) || 0) * (parent.height / (previewContainer.paperAspect >= 1.0 ? 210.0 : 297.0))))
                                anchors.leftMargin: Math.max(0, Math.min(parent.width * 0.25, (parseFloat(marginLeftInput.text) || 0) * (parent.width / (previewContainer.paperAspect >= 1.0 ? 297.0 : 210.0))))
                                anchors.rightMargin: Math.max(0, Math.min(parent.width * 0.25, (parseFloat(marginRightInput.text) || 0) * (parent.width / (previewContainer.paperAspect >= 1.0 ? 297.0 : 210.0))))
                                color: "transparent"
                                clip: true
                                visible: root.printPageList.length > 0

                                Grid {
                                    id: nupGrid
                                    anchors.fill: parent
                                    anchors.margins: 2
                                    columns: root.gridCols
                                    rows: root.gridRows
                                    spacing: root.nupCount > 1 ? 4 : 0

                                    Repeater {
                                        model: root.nupCount

                                        Item {
                                            width: (printableArea.width - 4 - (root.gridCols - 1) * nupGrid.spacing) / root.gridCols
                                            height: (printableArea.height - 4 - (root.gridRows - 1) * nupGrid.spacing) / root.gridRows

                                            property int slotPageListIndex: root.currentSheet * root.nupCount + index
                                            property int slotDocPageIndex: (slotPageListIndex < root.printPageList.length) ? root.printPageList[slotPageListIndex] : -1

                                            Rectangle {
                                                anchors.fill: parent
                                                color: "transparent"
                                                border.color: "#D0D0D0"
                                                border.width: root.nupCount > 1 ? 1 : 0
                                                visible: root.nupCount > 1 && slotDocPageIndex >= 0
                                            }

                                            Image {
                                                id: slotImage
                                                anchors.fill: parent
                                                anchors.margins: root.nupCount > 1 ? 2 : 0
                                                fillMode: Image.PreserveAspectFit
                                                asynchronous: true
                                                cache: false
                                                smooth: true
                                                mipmap: true
                                                visible: slotDocPageIndex >= 0
                                                transformOrigin: Item.Center
                                                scale: (root.nupCount === 1 && scaleCustom.checked) ? (root.customScaleValue / 100.0) : 1.0
                                                source: {
                                                    if (!pdfController.hasDocument || slotDocPageIndex < 0) return ""
                                                    var rot = 0
                                                    var geoms = pdfController.pageGeometries
                                                    if (geoms && geoms.length > slotDocPageIndex) {
                                                        rot = geoms[slotDocPageIndex].rotation || 0
                                                    }
                                                    var grayParam = grayscaleCheck.checked ? "&gray=1" : ""
                                                    return "image://pdf/" + pdfController.activeDocId + "/" + slotDocPageIndex +
                                                           "?zoom=0.6&rot=" + rot + grayParam + "&preview=1&v=" + pdfController.renderNonce
                                                }
                                            }

                                            // Badge showing page number in N-up mode
                                            Rectangle {
                                                anchors.bottom: parent.bottom
                                                anchors.right: parent.right
                                                anchors.margins: 3
                                                width: badgeText.width + 6
                                                height: 14
                                                radius: 2
                                                color: Qt.rgba(0, 0, 0, 0.6)
                                                visible: root.nupCount > 1 && slotDocPageIndex >= 0

                                                Text {
                                                    id: badgeText
                                                    anchors.centerIn: parent
                                                    text: (slotDocPageIndex + 1).toString()
                                                    font.pixelSize: 9
                                                    font.bold: true
                                                    color: "#FFFFFF"
                                                }
                                            }

                                            Text {
                                                anchors.centerIn: parent
                                                text: "[ Blank ]"
                                                font.pixelSize: 11
                                                font.italic: true
                                                color: "#AAAAAA"
                                                visible: root.nupCount > 1 && slotDocPageIndex < 0 && slotPageListIndex < root.printPageList.length
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Sheet / Page navigation
                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 8

                        Rectangle {
                            width: 26; height: 26
                            color: prevPageBtn.containsMouse ? Theme.buttonHover : Theme.cardBackground
                            border.color: Theme.borderSubtle; border.width: 1; radius: 3
                            Text { anchors.centerIn: parent; text: "◀"; font.pixelSize: 11; color: root.previewPage > 0 ? Theme.textPrimary : Theme.textDisabled }
                            MouseArea {
                                id: prevPageBtn; anchors.fill: parent; hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: if (root.previewPage > 0) root.previewPage--
                            }
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: {
                                if (root.printPageList.length === 0) return "No pages"
                                if (root.nupCount === 1) {
                                    return "Page " + (root.previewPage + 1) + " of " + root.totalSheets
                                }
                                return "Sheet " + (root.previewPage + 1) + " of " + root.totalSheets
                            }
                            font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                            color: Theme.textSecondary
                        }

                        Rectangle {
                            width: 26; height: 26
                            color: nextPageBtn.containsMouse ? Theme.buttonHover : Theme.cardBackground
                            border.color: Theme.borderSubtle; border.width: 1; radius: 3
                            Text { anchors.centerIn: parent; text: "▶"; font.pixelSize: 11; color: root.previewPage < root.totalSheets - 1 ? Theme.textPrimary : Theme.textDisabled }
                            MouseArea {
                                id: nextPageBtn; anchors.fill: parent; hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: if (root.previewPage < root.totalSheets - 1) root.previewPage++
                            }
                        }
                    }
                }
            }  // RIGHT rectangle
        }  // body Row

        // ── Bottom Action Bar ─────────────────────────────────────────────
        Rectangle {
            width: parent.width
            height: 48
            color: Theme.panelBackground

            // top divider
            Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: Theme.divider }

            Item {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16

                // Left: pages summary label
                Text {
                    anchors.left: parent.left
                    anchors.right: buttonRow.left
                    anchors.rightMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    text: root.printPageList.length > 0
                          ? root.printPageList.length + " page(s) to print  ·  " + root.copiesCount + " cop" + (root.copiesCount === 1 ? "y" : "ies")
                          : "0 pages to print"
                    font.pixelSize: Theme.fontSizeSmall
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                    elide: Text.ElideRight
                }

                // Right: Cancel + Print buttons
                Row {
                    id: buttonRow
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    OqButton {
                        text: "Cancel"
                        height: 30
                        width: 72
                        onClicked: root.close()
                    }

                    OqButton {
                        text: "Print"
                        isPrimary: true
                        height: 30
                        width: 72
                        enabled: root.printPageList.length > 0
                        onClicked: {
                            var settings = root._buildSettings()
                            root.close()
                            pdfController.printWithSettings(settings)
                        }
                    }
                }
            }
        }

    }  // root Column

    // ── Inline component definitions ───────────────────────────────────────

    component SectionHeader: Column {
        property string label: ""
        width: parent ? parent.width : 320
        spacing: 4
        topPadding: 4

        Text {
            text: parent.label
            font.pixelSize: Theme.fontSizeSmall
            font.weight: Font.Bold
            font.family: Theme.fontFamily
            font.letterSpacing: 0.5
            color: Theme.textSecondary
        }
        Rectangle {
            width: parent.width
            height: 1
            color: Theme.divider
        }
    }

    component SectionDivider: Item {
        width: parent ? parent.width : 320
        height: 10
    }

    component MarginInput: Rectangle {
        width: 56; height: 24
        color: Theme.inputBackground
        border.color: Theme.borderSubtle; border.width: 1; radius: 3
        property alias text: ti.text

        TextInput {
            id: ti
            anchors.fill: parent; anchors.margins: 4
            font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
            color: Theme.textPrimary
            text: "0"
            inputMethodHints: Qt.ImhFormattedNumbersOnly
            validator: RegularExpressionValidator { regularExpression: /^[0-9]{0,2}(\.[0-9]{0,1})?$/ }
        }
    }

}  // Dialog
