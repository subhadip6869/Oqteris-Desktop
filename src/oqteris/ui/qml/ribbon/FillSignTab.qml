import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: AcroForms
    OqRibbonGroup {
        title: "Forms"

        OqRibbonButton {
            text: "Reset Form"
            iconName: "rotate"
            tooltipText: "Reset Form Fields to Defaults"
            enabled: pdfController.hasDocument
            onClicked: {
                // Reset form fields
            }
        }
    }

    // Group 2: Visual Signatures
    OqRibbonGroup {
        title: "Signatures"

        OqRibbonButton {
            text: "Draw Signature"
            iconName: "draw"
            tooltipText: "Draw and Place Visual Signature"
            enabled: pdfController.hasDocument
            onClicked: ribbonController.selectTool("ink")
        }

        OqRibbonButton {
            text: "Digital Sign"
            iconName: "signatures"
            tooltipText: "Cryptographically Sign PDF with Certificate"
            enabled: pdfController.hasDocument
            onClicked: signDialogLoader.openSignDialog()
        }

        OqRibbonButton {
            text: "Signature Panel"
            iconName: "sidebar"
            tooltipText: "Open Digital Signatures Panel"
            enabled: pdfController.hasDocument
            onClicked: {
                signatureController.inspectSignatures()
                mainPanelState.showLeftPanel = true
                mainPanelState.currentPanelTab = "signatures"
            }
        }

        OqRibbonButton {
            text: "Validate All"
            iconName: "shield"
            tooltipText: "Validate All Digital Signatures"
            enabled: pdfController.hasDocument
            onClicked: signatureController.inspectSignatures()
        }
    }
}
