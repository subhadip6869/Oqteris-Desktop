import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: Digital Security
    OqRibbonGroup {
        title: "Digital Signatures"

        OqRibbonButton {
            text: "Sign PDF"
            iconSymbol: "🔏"
            tooltipText: "Add Cryptographic Digital Signature"
            enabled: pdfController.hasDocument
            onClicked: signDialogLoader.openSignDialog()
        }

        OqRibbonButton {
            text: "Validate"
            iconSymbol: "🛡"
            tooltipText: "Inspect and Validate Signatures"
            enabled: pdfController.hasDocument
            onClicked: {
                signatureController.inspectSignatures()
                mainPanelState.showLeftPanel = true
                mainPanelState.currentPanelTab = "signatures"
            }
        }
    }

    // Group 2: Certificates & Trust
    OqRibbonGroup {
        title: "Trust Management"

        OqRibbonButton {
            text: "Certificates"
            iconSymbol: "📜"
            tooltipText: "Manage Trusted Root Certificates"
            onClicked: {
                mainPanelState.showLeftPanel = true
                mainPanelState.currentPanelTab = "signatures"
            }
        }
    }
}
