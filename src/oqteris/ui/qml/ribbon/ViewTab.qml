import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: Display Modes
    OqRibbonGroup {
        title: "Page Display"

        OqRibbonButton {
            text: "Continuous"
            iconSymbol: "📜"
            tooltipText: "Continuous Scrolling Mode"
            isChecked: pdfController.displayMode === "continuous"
            enabled: pdfController.hasDocument
            onClicked: pdfController.displayMode = "continuous"
        }

        OqRibbonButton {
            text: "Single Page"
            iconSymbol: "📄"
            tooltipText: "Single Page Display"
            isChecked: pdfController.displayMode === "single"
            enabled: pdfController.hasDocument
            onClicked: pdfController.displayMode = "single"
        }
    }

    // Group 2: Navigation Panels
    OqRibbonGroup {
        title: "Panels"

        OqRibbonButton {
            text: "Thumbnails"
            iconSymbol: "🖼"
            tooltipText: "Page Thumbnails Panel"
            isChecked: mainPanelState.showLeftPanel && mainPanelState.currentPanelTab === "thumbnails"
            onClicked: mainPanelState.togglePanel("thumbnails")
        }

        OqRibbonButton {
            text: "Bookmarks"
            iconSymbol: "📑"
            tooltipText: "Document Bookmarks"
            isChecked: mainPanelState.showLeftPanel && mainPanelState.currentPanelTab === "bookmarks"
            onClicked: mainPanelState.togglePanel("bookmarks")
        }

        OqRibbonButton {
            text: "Annotations"
            iconSymbol: "💬"
            tooltipText: "Comments & Annotations"
            isChecked: mainPanelState.showLeftPanel && mainPanelState.currentPanelTab === "annotations"
            onClicked: mainPanelState.togglePanel("annotations")
        }

        OqRibbonButton {
            text: "Signatures"
            iconSymbol: "🔏"
            tooltipText: "Digital Signatures List"
            isChecked: mainPanelState.showLeftPanel && mainPanelState.currentPanelTab === "signatures"
            onClicked: {
                signatureController.inspectSignatures()
                mainPanelState.togglePanel("signatures")
            }
        }

        OqRibbonButton {
            text: "Properties"
            iconSymbol: "ℹ"
            tooltipText: "Document Properties"
            isChecked: mainPanelState.showRightPanel
            onClicked: mainPanelState.showRightPanel = !mainPanelState.showRightPanel
        }
    }

    // Group 3: Search
    OqRibbonGroup {
        title: "Find"

        OqRibbonButton {
            text: "Search"
            iconSymbol: "🔎"
            tooltipText: "Find Text in Document"
            shortcutText: "Ctrl+F"
            enabled: pdfController.hasDocument
            onClicked: {
                mainPanelState.showLeftPanel = true
                mainPanelState.currentPanelTab = "search"
            }
        }
    }
}
