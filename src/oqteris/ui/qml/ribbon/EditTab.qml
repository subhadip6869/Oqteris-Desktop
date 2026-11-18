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
            iconName: "select-text"
            tooltipText: "Insert Text into PDF"
            isChecked: ribbonController.activeTool === "add_text"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("add_text")
        }

        OqRibbonButton {
            text: "Add Image"
            iconName: "thumbnails"
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
            iconName: "share"
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
            iconName: "draw"
            tooltipText: "Direct Text Editing & Replacement"
            isChecked: ribbonController.activeTool === "edit_text"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("edit_text")
        }
    }
}
