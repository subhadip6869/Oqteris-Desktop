import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: File Operations
    OqRibbonGroup {
        title: "File"

        OqRibbonButton {
            text: "Open"
            iconSymbol: "📂"
            tooltipText: "Open PDF Document"
            shortcutText: "Ctrl+O"
            onClicked: fileDialogLoader.openFile()
        }

        OqRibbonButton {
            text: "Save"
            iconSymbol: "💾"
            tooltipText: "Save Document"
            shortcutText: "Ctrl+S"
            enabled: pdfController.hasDocument && pdfController.isModified
            onClicked: pdfController.saveDocument()
        }

        OqRibbonButton {
            text: "Save As"
            iconSymbol: "📑"
            tooltipText: "Save Document As..."
            shortcutText: "Ctrl+Shift+S"
            enabled: pdfController.hasDocument
            onClicked: fileDialogLoader.saveFileAs()
        }
    }

    // Group 2: History (Undo/Redo)
    OqRibbonGroup {
        title: "History"

        OqRibbonButton {
            text: "Undo"
            iconSymbol: "↩"
            tooltipText: "Undo"
            shortcutText: "Ctrl+Z"
            enabled: ribbonController.canUndo
            onClicked: ribbonController.undo()
        }

        OqRibbonButton {
            text: "Redo"
            iconSymbol: "↪"
            tooltipText: "Redo"
            shortcutText: "Ctrl+Y"
            enabled: ribbonController.canRedo
            onClicked: ribbonController.redo()
        }
    }

    // Group 3: Basic Tools
    OqRibbonGroup {
        title: "Tools"

        OqRibbonButton {
            text: "Select"
            iconSymbol: "👆"
            tooltipText: "Select Text and Objects"
            isChecked: ribbonController.activeTool === "select"
            onClicked: ribbonController.selectTool("select")
        }

        OqRibbonButton {
            text: "Hand"
            iconSymbol: "✋"
            tooltipText: "Hand Pan Tool"
            isChecked: ribbonController.activeTool === "hand"
            onClicked: ribbonController.selectTool("hand")
        }
    }

    // Group 4: Zoom Controls
    OqRibbonGroup {
        title: "Zoom"

        OqRibbonButton {
            text: "Zoom In"
            iconSymbol: "🔍+"
            tooltipText: "Zoom In"
            shortcutText: "Ctrl++"
            enabled: pdfController.hasDocument
            onClicked: pdfController.zoomIn()
        }

        OqRibbonButton {
            text: "Zoom Out"
            iconSymbol: "🔍-"
            tooltipText: "Zoom Out"
            shortcutText: "Ctrl+-"
            enabled: pdfController.hasDocument
            onClicked: pdfController.zoomOut()
        }

        OqRibbonButton {
            text: "100%"
            iconSymbol: "1:1"
            tooltipText: "Actual Size"
            shortcutText: "Ctrl+1"
            enabled: pdfController.hasDocument
            onClicked: pdfController.actualSize()
        }

        OqRibbonButton {
            text: "Fit Width"
            iconSymbol: "↔"
            tooltipText: "Fit to Width"
            shortcutText: "Ctrl+2"
            enabled: pdfController.hasDocument
            onClicked: pdfController.fitWidth(documentWorkspace.viewportWidth)
        }

        OqRibbonButton {
            text: "Fit Page"
            iconSymbol: "↕"
            tooltipText: "Fit Entire Page"
            shortcutText: "Ctrl+0"
            enabled: pdfController.hasDocument
            onClicked: pdfController.fitPage(documentWorkspace.viewportWidth, documentWorkspace.viewportHeight)
        }
    }

    // Group 5: Page Rotation
    OqRibbonGroup {
        title: "Rotate"

        OqRibbonButton {
            text: "Rotate 90°"
            iconSymbol: "↻"
            tooltipText: "Rotate Page Clockwise"
            shortcutText: "Ctrl+R"
            enabled: pdfController.hasDocument
            onClicked: pdfController.rotatePage(90)
        }
    }
}
