import QtQuick
import QtQuick.Controls.Basic
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
            spacing: 12
            CheckBox {
                id: compressImagesCheck
                text: "Compress Images"
                checked: true
            }
            CheckBox {
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

            Slider {
                id: qualitySlider
                from: 20
                to: 95
                value: 75
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
                Button {
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

            Button {
                text: "Compress"
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

            Button {
                text: "Close"
                onClicked: root.close()
            }
        }
    }

    function setOutPath(path) { optOutInput.text = path }
}
