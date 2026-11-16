import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: Text Markup
    OqRibbonGroup {
        title: "Text Markup"

        OqRibbonButton {
            text: "Highlight"
            iconSymbol: "🖍"
            tooltipText: "Highlight Selected Text"
            isChecked: ribbonController.activeTool === "highlight"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("highlight")
        }

        OqRibbonButton {
            text: "Underline"
            iconSymbol: "<u>U</u>"
            tooltipText: "Underline Selected Text"
            isChecked: ribbonController.activeTool === "underline"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("underline")
        }

        OqRibbonButton {
            text: "Strikeout"
            iconSymbol: "<s>S</s>"
            tooltipText: "Strikethrough Selected Text"
            isChecked: ribbonController.activeTool === "strikeout"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("strikeout")
        }
    }

    // Group 2: Annotations
    OqRibbonGroup {
        title: "Annotations"

        OqRibbonButton {
            text: "Sticky Note"
            iconSymbol: "📝"
            tooltipText: "Place a Sticky Comment Note"
            isChecked: ribbonController.activeTool === "note"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("note")
        }

        OqRibbonButton {
            text: "Freehand"
            iconSymbol: "✒"
            tooltipText: "Freehand Ink Drawing"
            isChecked: ribbonController.activeTool === "ink"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("ink")
        }
    }

    // Group 3: Geometric Shapes
    OqRibbonGroup {
        title: "Shapes"

        OqRibbonButton {
            text: "Rectangle"
            iconSymbol: "▭"
            tooltipText: "Draw Rectangle"
            isChecked: ribbonController.activeTool === "rectangle"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("rectangle")
        }

        OqRibbonButton {
            text: "Circle"
            iconSymbol: "◯"
            tooltipText: "Draw Circle / Oval"
            isChecked: ribbonController.activeTool === "circle"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("circle")
        }

        OqRibbonButton {
            text: "Line"
            iconSymbol: "╱"
            tooltipText: "Draw Line"
            isChecked: ribbonController.activeTool === "line"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("line")
        }

        OqRibbonButton {
            text: "Arrow"
            iconSymbol: "➔"
            tooltipText: "Draw Pointer Arrow"
            isChecked: ribbonController.activeTool === "arrow"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("arrow")
        }
    }

    // Group 4: Stamps
    OqRibbonGroup {
        title: "Stamps"

        OqRibbonButton {
            text: "Approved"
            iconSymbol: "✔"
            tooltipText: "Approved Stamp"
            isChecked: ribbonController.activeTool === "stamp_approved"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("stamp_approved")
        }

        OqRibbonButton {
            text: "Confidential"
            iconSymbol: "🔒"
            tooltipText: "Confidential Stamp"
            isChecked: ribbonController.activeTool === "stamp_confidential"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("stamp_confidential")
        }
    }
}
