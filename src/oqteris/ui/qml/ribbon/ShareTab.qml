import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: Share
    OqRibbonGroup {
        title: "Share"

        OqRibbonButton {
            text: "Share\nDocument"
            iconName: "share"
            tooltipText: "Share or Export Document"
            enabled: pdfController.hasDocument
            onClicked: fileDialogLoader.saveFileAs()
        }

        OqRibbonButton {
            text: "Save\nCopy"
            iconName: "save-as"
            tooltipText: "Save Document Copy"
            enabled: pdfController.hasDocument
            onClicked: fileDialogLoader.saveFileAs()
        }
    }

    // Group 2: Document Info
    OqRibbonGroup {
        title: "Info"

        OqRibbonButton {
            text: "Document\nProperties"
            iconName: "properties"
            tooltipText: "View Document Metadata and Security"
            enabled: pdfController.hasDocument
            isChecked: mainPanelState.showRightPanel
            onClicked: mainPanelState.showRightPanel = !mainPanelState.showRightPanel
        }
    }
}
