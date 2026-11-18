import QtQuick
import QtQuick.Controls.Basic
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: File Operations
    OqRibbonGroup {
        title: "File"

        // Open PDF (Large button)
        OqRibbonButton {
            text: "Open\nPDF"
            iconName: "folder-open"
            tooltipText: "Open PDF Document"
            shortcutText: "Ctrl+O"
            onClicked: fileDialogLoader.openFile()
        }

        // Two items in a column (Save & Save As)
        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            OqRibbonButton {
                text: "Save"
                iconName: "save"
                isLarge: false
                tooltipText: "Save Document"
                shortcutText: "Ctrl+S"
                enabled: pdfController.hasDocument && pdfController.isModified
                onClicked: pdfController.saveDocument()
            }

            OqRibbonButton {
                text: "Save As"
                iconName: "save-as"
                isLarge: false
                tooltipText: "Save Document As..."
                shortcutText: "Ctrl+Shift+S"
                enabled: pdfController.hasDocument
                onClicked: fileDialogLoader.saveFileAs()
            }
        }

        // Print (Large button)
        OqRibbonButton {
            text: "Print"
            iconName: "print"
            tooltipText: "Print Document"
            shortcutText: "Ctrl+P"
            enabled: pdfController.hasDocument
            onClicked: {
                // Trigger print dialog or notification
                signatureController.requestStatusMessage("Print", "Printing dialog prepared for " + pdfController.fileName)
            }
        }
    }

    // Group 2: Clipboard
    OqRibbonGroup {
        title: "Clipboard"

        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            OqRibbonButton {
                text: "Copy"
                iconName: "copy"
                isLarge: false
                tooltipText: "Copy Selected Text"
                shortcutText: "Ctrl+C"
                enabled: pdfController.hasDocument
                onClicked: {
                    // Copy action
                }
            }

            OqRibbonButton {
                text: "Select All"
                iconName: "select-all"
                isLarge: false
                tooltipText: "Select All Page Content"
                shortcutText: "Ctrl+A"
                enabled: pdfController.hasDocument
                onClicked: {
                    // Select all action
                }
            }
        }
    }

    // Group 3: Tools (Selection & Pan)
    OqRibbonGroup {
        title: "Tools"

        OqRibbonButton {
            text: "Select\nText"
            iconName: "select-text"
            tooltipText: "Select Text and Elements"
            isChecked: ribbonController.activeTool === "select"
            onClicked: ribbonController.selectTool("select")
        }

        OqRibbonButton {
            text: "Hand\nTool"
            iconName: "hand"
            tooltipText: "Hand Pan Tool"
            isChecked: ribbonController.activeTool === "hand"
            onClicked: ribbonController.selectTool("hand")
        }
    }

    // Group 4: Navigation
    OqRibbonGroup {
        title: "Navigation"

        Row {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 4

            OqToolButton {
                iconName: "first-page"
                tooltipText: "First Page"
                enabled: pdfController.hasDocument && pdfController.currentPage > 0
                onClicked: pdfController.firstPage()
            }

            OqToolButton {
                iconName: "prev-page"
                tooltipText: "Previous Page"
                enabled: pdfController.hasDocument && pdfController.currentPage > 0
                onClicked: pdfController.prevPage()
            }

            // Current Page Input Pill
            Rectangle {
                width: Math.max(34, pageInput.implicitWidth + 14)
                height: 24
                radius: 4
                color: appController.isDarkMode ? "#272A30" : "#F1F5F9"
                border.color: pageInput.activeFocus ? Theme.borderFocused : Theme.borderSubtle
                border.width: 1
                anchors.verticalCenter: parent.verticalCenter

                TextInput {
                    id: pageInput
                    anchors.fill: parent
                    anchors.margins: 2
                    horizontalAlignment: TextInput.AlignHCenter
                    verticalAlignment: TextInput.AlignVCenter
                    font.pixelSize: 11
                    font.bold: true
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                    text: pdfController.hasDocument ? (pdfController.currentPage + 1).toString() : "1"
                    selectByMouse: true
                    validator: IntValidator { bottom: 1; top: Math.max(1, pdfController.pageCount) }
                    onAccepted: {
                        var target = parseInt(text) - 1;
                        if (!isNaN(target) && target >= 0 && target < pdfController.pageCount) {
                            pdfController.goToPage(target);
                        }
                    }
                }
            }

            Text {
                text: pdfController.hasDocument ? ("... " + pdfController.pageCount) : "..."
                font.pixelSize: 11
                font.family: Theme.fontFamily
                color: Theme.textSecondary
                anchors.verticalCenter: parent.verticalCenter
            }

            OqToolButton {
                iconName: "next-page"
                tooltipText: "Next Page"
                enabled: pdfController.hasDocument && pdfController.currentPage < pdfController.pageCount - 1
                onClicked: pdfController.nextPage()
            }

            OqToolButton {
                iconName: "last-page"
                tooltipText: "Last Page"
                enabled: pdfController.hasDocument && pdfController.currentPage < pdfController.pageCount - 1
                onClicked: pdfController.lastPage()
            }
        }
    }

    // Group 5: Zoom Controls
    OqRibbonGroup {
        title: "Zoom"

        OqRibbonButton {
            text: "Actual\nSize"
            iconName: "actual-size"
            tooltipText: "Actual Size (100%)"
            shortcutText: "Ctrl+1"
            enabled: pdfController.hasDocument
            onClicked: pdfController.actualSize()
        }

        OqRibbonButton {
            text: "Fit\nPage"
            iconName: "fit-page"
            tooltipText: "Fit Entire Page in Window"
            shortcutText: "Ctrl+0"
            enabled: pdfController.hasDocument
            onClicked: pdfController.fitPage(documentWorkspace.viewportWidth, documentWorkspace.viewportHeight)
        }

        OqRibbonButton {
            text: "Fit\nWidth"
            iconName: "fit-width"
            tooltipText: "Fit Page Width"
            shortcutText: "Ctrl+2"
            enabled: pdfController.hasDocument
            onClicked: pdfController.fitWidth(documentWorkspace.viewportWidth)
        }

        // Two items in a column (Zoom In & Zoom Out)
        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            OqRibbonButton {
                text: "Zoom In"
                iconName: "zoom-in"
                isLarge: false
                tooltipText: "Zoom In"
                shortcutText: "Ctrl++"
                enabled: pdfController.hasDocument
                onClicked: pdfController.zoomIn()
            }

            OqRibbonButton {
                text: "Zoom Out"
                iconName: "zoom-out"
                isLarge: false
                tooltipText: "Zoom Out"
                shortcutText: "Ctrl+-"
                enabled: pdfController.hasDocument
                onClicked: pdfController.zoomOut()
            }
        }

        // Presets Dropdown
        OqRibbonButton {
            id: presetsBtn
            text: "Presets"
            iconName: "presets"
            hasDropdown: true
            tooltipText: "Select Zoom Level Preset"
            enabled: pdfController.hasDocument
            onClicked: presetsMenu.open()

            Menu {
                id: presetsMenu
                y: presetsBtn.height

                MenuItem { text: "50%"; onClicked: pdfController.setZoom(0.5) }
                MenuItem { text: "75%"; onClicked: pdfController.setZoom(0.75) }
                MenuItem { text: "100%"; onClicked: pdfController.setZoom(1.0) }
                MenuItem { text: "125%"; onClicked: pdfController.setZoom(1.25) }
                MenuItem { text: "150%"; onClicked: pdfController.setZoom(1.5) }
                MenuItem { text: "200%"; onClicked: pdfController.setZoom(2.0) }
                MenuItem { text: "300%"; onClicked: pdfController.setZoom(3.0) }
            }
        }
    }

    // Group 6: Page Tools
    OqRibbonGroup {
        title: "Page Tools"

        OqRibbonButton {
            id: rotateBtn
            text: "Rotate"
            iconName: "rotate"
            hasDropdown: true
            tooltipText: "Rotate Page"
            shortcutText: "Ctrl+R"
            enabled: pdfController.hasDocument
            onClicked: rotateMenu.open()

            Menu {
                id: rotateMenu
                y: rotateBtn.height

                MenuItem { text: "Rotate 90° Clockwise"; onClicked: pdfController.rotatePage(90) }
                MenuItem { text: "Rotate 180°"; onClicked: pdfController.rotatePage(180) }
                MenuItem { text: "Rotate 90° Counter-Clockwise"; onClicked: pdfController.rotatePage(270) }
            }
        }
    }

    // Group 7: Sidebar Layout
    OqRibbonGroup {
        title: ""

        OqRibbonButton {
            text: "Sidebar"
            iconName: "sidebar"
            tooltipText: "Toggle Navigation Sidebar"
            isChecked: mainPanelState.showLeftPanel
            onClicked: {
                if (mainPanelState.showLeftPanel) {
                    mainPanelState.showLeftPanel = false;
                } else {
                    mainPanelState.showLeftPanel = true;
                    if (!mainPanelState.currentPanelTab) {
                        mainPanelState.currentPanelTab = "thumbnails";
                    }
                }
            }
        }
    }

    // Group 8: Find
    OqRibbonGroup {
        title: "Find"

        OqRibbonButton {
            text: "Find"
            iconName: "find"
            tooltipText: "Search Text in Document"
            shortcutText: "Ctrl+F"
            enabled: pdfController.hasDocument
            onClicked: {
                mainPanelState.showLeftPanel = true;
                mainPanelState.currentPanelTab = "search";
            }
        }
    }

    // Group 9: Security / Trust Store
    OqRibbonGroup {
        title: "Security"

        OqRibbonButton {
            text: signatureController.hasSignatures
                ? (signatureController.allValidAndTrusted ? "Signed\n(Valid)" : "Signed\n(Check)")
                : "Unsigned\nDocument"
            iconName: "shield"
            tooltipText: signatureController.hasSignatures ? "Inspect Digital Signatures" : "Open Security & Trust Store"
            enabled: true
            onClicked: {
                if (signatureController.hasSignatures) {
                    mainPanelState.showLeftPanel = true;
                    mainPanelState.currentPanelTab = "signatures";
                } else {
                    trustStoreDialogLoader.openTrustStoreDialog();
                }
            }
        }
    }
}
