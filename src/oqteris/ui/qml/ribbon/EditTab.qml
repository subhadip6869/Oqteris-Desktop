import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: Content Tools
    OqRibbonGroup {
        title: "Insert"

        OqRibbonButton {
            text: "Add Text"
            iconSymbol: "🔤"
            tooltipText: "Insert Text into PDF"
            isChecked: ribbonController.activeTool === "add_text"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("add_text")
        }

        OqRibbonButton {
            text: "Add Image"
            iconSymbol: "🖼"
            tooltipText: "Insert Image into Page"
            isChecked: ribbonController.activeTool === "add_image"
            enabled: pdfController.hasDocument
            onClicked: {
                ribbonController.selectTool("add_image")
                fileDialogLoader.openImageToInsert()
            }
        }

        OqRibbonButton {
            text: "Add Link"
            iconSymbol: "🔗"
            tooltipText: "Create Hyperlink"
            isChecked: ribbonController.activeTool === "add_link"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("add_link")
        }
    }

    // Group 2: Text Modification
    OqRibbonGroup {
        title: "Content"

        OqRibbonButton {
            text: "Edit Text"
            iconSymbol: "✏"
            tooltipText: "Direct Text Editing & Replacement"
            isChecked: ribbonController.activeTool === "edit_text"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("edit_text")
        }
    }
}
