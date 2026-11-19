import QtQuick
import QtQuick.Controls
import "../components"
import "../themes"

Dialog {
    id: root
    width: 440
    height: 340
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
            text: "Reduce PDF File Size"
            font.pixelSize: Theme.fontSizeNormal
            font.weight: Font.DemiBold
            color: Theme.textPrimary
        }

        Row {
            spacing: 16
            OqCheckBox {
                id: compressImagesCheck
                text: "Compress Images"
                checked: true
            }
            OqCheckBox {
                id: removeMetaCheck
                text: "Remove Metadata"
                checked: false
            }
        }

        Row {
            spacing: 12
            visible: compressImagesCheck.checked
            Text {
                text: "Image Quality: " + Math.round(qualitySlider.value) + "%"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textPrimary
                width: 140
                anchors.verticalCenter: parent.verticalCenter
            }

            OqSlider {
                id: qualitySlider
                from: 20
                to: 95
                value: 75
                width: 160
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Column {
            width: parent.width
            spacing: 4
            Text { text: "Save Optimized PDF As:"; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
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
                        id: optOutInput
                        anchors.fill: parent
                        anchors.margins: 4
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textPrimary
                    }
                }
                OqButton {
                    text: "Browse"
                    height: 28
                    onClicked: fileDialogLoader.saveOptimizedFileAs()
                }
            }
        }

        Text {
            id: resultText
            text: ""
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.statusSuccess
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 12

            OqButton {
                text: "Compress"
                isPrimary: true
                enabled: optOutInput.text.length > 0
                onClicked: {
                    var res = organizeController.compressPdf(
                        optOutInput.text,
                        compressImagesCheck.checked,
                        Math.round(qualitySlider.value),
                        removeMetaCheck.checked
                    )
                    if (res && res.savedBytes) {
                        resultText.text = "Saved " + res.compressionRatio + "% (" + Math.round(res.savedBytes / 1024) + " KB)"
                    }
                }
            }

            OqButton {
                text: "Close"
                onClicked: root.close()
            }
        }
    }

    function setOutPath(path) { optOutInput.text = path }
}
