import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: Export
    OqRibbonGroup {
        title: "Export"

        OqRibbonButton {
            text: "To Images"
            iconSymbol: "🖼"
            tooltipText: "Export PDF Pages as PNG Images"
            enabled: pdfController.hasDocument
            onClicked: fileDialogLoader.selectExportImagesDir()
        }

        OqRibbonButton {
            text: "Images to PDF"
            iconSymbol: "📄+"
            tooltipText: "Create PDF from Multiple Images"
            onClicked: fileDialogLoader.openImagesToConvert()
        }
    }

    // Group 2: Document Processing
    OqRibbonGroup {
        title: "Processing"

        OqRibbonButton {
            text: "OCR Text"
            iconSymbol: "🔍T"
            tooltipText: "Recognize Scanned Text via OCR"
            enabled: pdfController.hasDocument
            onClicked: ocrDialogLoader.openOcrDialog()
        }

        OqRibbonButton {
            text: "Compress"
            iconSymbol: "🗜"
            tooltipText: "Optimize and Compress PDF File Size"
            enabled: pdfController.hasDocument
            onClicked: optimizeDialogLoader.openOptimizeDialog()
        }
    }
}
