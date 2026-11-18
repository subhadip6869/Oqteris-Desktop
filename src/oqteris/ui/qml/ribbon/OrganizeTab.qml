import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: Page Operations
    OqRibbonGroup {
        title: "Pages"

        OqRibbonButton {
            text: "Delete Page"
            iconName: "delete"
            tooltipText: "Delete Current Page"
            enabled: pdfController.hasDocument && pdfController.pageCount > 1
            onClicked: organizeController.deletePage(pdfController.currentPage)
        }

        OqRibbonButton {
            text: "Extract Page"
            iconName: "extract"
            tooltipText: "Extract Current Page to New PDF"
            enabled: pdfController.hasDocument
            onClicked: fileDialogLoader.saveExtractedPage()
        }

        OqRibbonButton {
            text: "Rotate"
            iconName: "rotate"
            tooltipText: "Rotate Page 90° Clockwise"
            enabled: pdfController.hasDocument
            onClicked: pdfController.rotatePage(90)
        }
    }

    // Group 2: Document Structure
    OqRibbonGroup {
        title: "Combine & Split"

        OqRibbonButton {
            text: "Merge PDFs"
            iconName: "merge"
            tooltipText: "Combine Multiple PDFs into One"
            onClicked: fileDialogLoader.openPdfsToMerge()
        }

        OqRibbonButton {
            text: "Split PDF"
            iconName: "split"
            tooltipText: "Split Document into Parts"
            enabled: pdfController.hasDocument && pdfController.pageCount > 1
            onClicked: fileDialogLoader.selectSplitOutputDir()
        }
    }
}
