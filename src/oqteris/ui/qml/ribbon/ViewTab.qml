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
            iconName: "continuous"
            tooltipText: "Continuous Scrolling Mode"
            isChecked: pdfController.displayMode === "continuous"
            enabled: pdfController.hasDocument
            onClicked: pdfController.displayMode = "continuous"
        }

        OqRibbonButton {
            text: "Single Page"
            iconName: "single-page"
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
            iconName: "thumbnails"
            tooltipText: "Page Thumbnails Panel"
            isChecked: mainPanelState.showLeftPanel && mainPanelState.currentPanelTab === "thumbnails"
            onClicked: mainPanelState.togglePanel("thumbnails")
        }

        OqRibbonButton {
            text: "Bookmarks"
            iconName: "bookmarks"
            tooltipText: "Document Bookmarks"
            isChecked: mainPanelState.showLeftPanel && mainPanelState.currentPanelTab === "bookmarks"
            onClicked: mainPanelState.togglePanel("bookmarks")
        }

        OqRibbonButton {
            text: "Annotations"
            iconName: "annotations"
            tooltipText: "Comments & Annotations"
            isChecked: mainPanelState.showLeftPanel && mainPanelState.currentPanelTab === "annotations"
            onClicked: mainPanelState.togglePanel("annotations")
        }

        OqRibbonButton {
            text: "Signatures"
            iconName: "signatures"
            tooltipText: "Digital Signatures List"
            isChecked: mainPanelState.showLeftPanel && mainPanelState.currentPanelTab === "signatures"
            onClicked: {
                signatureController.inspectSignatures()
                mainPanelState.togglePanel("signatures")
            }
        }

        OqRibbonButton {
            text: "Properties"
            iconName: "properties"
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
            iconName: "find"
            tooltipText: "Find Text in Document"
            shortcutText: "Ctrl+F"
            enabled: pdfController.hasDocument
            onClicked: {
                mainPanelState.showLeftPanel = true
                mainPanelState.currentPanelTab = "search"
            }
        }
    }

    // Group 4: Theme & Appearance (Moved here from Help as requested)
    OqRibbonGroup {
        title: "Theme"

        OqRibbonButton {
            text: appController.isDarkMode ? "Light\nMode" : "Dark\nMode"
            iconName: appController.isDarkMode ? "theme-light" : "theme-dark"
            tooltipText: "Toggle Light / Dark Theme"
            onClicked: appController.toggleTheme()
        }
    }
}
