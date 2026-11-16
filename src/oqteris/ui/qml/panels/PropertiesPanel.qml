import QtQuick
import "../themes"

Rectangle {
    id: root
    width: 260
    color: Theme.panelBackground
    border.color: Theme.borderSubtle
    border.width: 1

    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12

        Row {
            width: parent.width
            Text {
                text: "Document Properties"
                font.pixelSize: Theme.fontSizeMedium
                font.weight: Font.DemiBold
                color: Theme.textPrimary
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.divider
        }

        Flickable {
            width: parent.width
            height: parent.height - 50
            contentHeight: propCol.implicitHeight
            boundsBehavior: Flickable.StopAtBounds
            clip: true

            Column {
                id: propCol
                width: parent.width
                spacing: 10

                Repeater {
                    model: [
                        { label: "Title", val: pdfController.metadata.title || "Untitled" },
                        { label: "Author", val: pdfController.metadata.author || "Unknown" },
                        { label: "Subject", val: pdfController.metadata.subject || "-" },
                        { label: "Format", val: pdfController.metadata.formatVersion || "PDF-1.7" },
                        { label: "Pages", val: pdfController.pageCount.toString() },
                        { label: "Encrypted", val: pdfController.metadata.isEncrypted ? "Yes" : "No" },
                        { label: "Digitally Signed", val: pdfController.metadata.isSigned ? "Yes" : "No" },
                        { label: "Location", val: pdfController.filePath || "-" }
                    ]

                    Column {
                        width: parent.width
                        spacing: 2

                        Text {
                            text: modelData.label
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }

                        Text {
                            text: modelData.val
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textPrimary
                            wrapMode: Text.WrapAnywhere
                            width: parent.width
                        }
                    }
                }
            }
        }
    }
}
