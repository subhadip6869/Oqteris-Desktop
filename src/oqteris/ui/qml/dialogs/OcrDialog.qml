import QtQuick
import QtQuick.Controls
import "../components"
import "../themes"

Dialog {
    id: root
    width: 460
    height: 380
    modal: true
    anchors.centerIn: parent

    background: Rectangle {
        color: Theme.cardBackground
        border.color: Theme.borderSubtle
        border.width: 1
        radius: 6
    }

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Text {
            text: "Generate Searchable PDF with OCR"
            font.pixelSize: Theme.fontSizeNormal
            font.weight: Font.DemiBold
            color: Theme.textPrimary
        }

        Text {
            text: ocrController.isTesseractAvailable ?
                "Tesseract engine detected." :
                "Warning: Tesseract not found in PATH. Please install Tesseract or specify path in Settings."
            font.pixelSize: Theme.fontSizeSmall
            color: ocrController.isTesseractAvailable ? Theme.statusSuccess : Theme.statusWarning
        }

        Row {
            spacing: 16
            OqCheckBox {
                id: deskewCheck
                text: "OpenCV Deskew"
                checked: true
            }
            OqCheckBox {
                id: binarizeCheck
                text: "Enhance Contrast"
                checked: false
            }
        }

        Column {
            width: parent.width
            spacing: 4
            Text { text: "Save Searchable PDF As:"; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
            Row {
                width: parent.width
                spacing: 6
                Rectangle {
                    width: parent.width - 80
                    height: 28
                    color: Theme.windowBackground
                    border.color: Theme.borderSubtle
                    border.width: 1
                    radius: 3
                    TextInput {
                        id: ocrOutInput
                        anchors.fill: parent
                        anchors.margins: 4
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textPrimary
                    }
                }
                OqButton {
                    text: "Browse"
                    height: 28
                    onClicked: fileDialogLoader.saveOcrFileAs()
                }
            }
        }

        // Progress display
        Column {
            width: parent.width
            spacing: 4
            visible: progressText.text.length > 0

            Text {
                id: progressText
                text: ""
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.brandPrimary
            }

            ProgressBar {
                id: progressBar
                width: parent.width
                from: 0
                to: 100
                value: 0
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 12

            OqButton {
                text: "Start OCR"
                isPrimary: true
                enabled: ocrController.isTesseractAvailable && ocrOutInput.text.length > 0
                onClicked: {
                    ocrController.runOcr(
                        ocrOutInput.text,
                        ["eng"],
                        deskewCheck.checked,
                        binarizeCheck.checked
                    )
                }
            }

            OqButton {
                text: "Cancel"
                onClicked: {
                    ocrController.cancelOcr()
                    root.close()
                }
            }
        }
    }

    Connections {
        target: ocrController
        function onOcrProgress(cur, tot, msg) {
            progressBar.value = (cur / tot) * 100
            progressText.text = msg
        }
        function onOcrFinished(msg, success) {
            progressText.text = success ? "OCR completed successfully!" : ("Error: " + msg)
            if (success) {
                root.close()
            }
        }
    }

    function setOutPath(path) { ocrOutInput.text = path }
}
