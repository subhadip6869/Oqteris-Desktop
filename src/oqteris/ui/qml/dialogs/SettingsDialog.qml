import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Dialog {
    id: root
    title: "Settings"
    width: 480
    height: 420
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
        spacing: 14

        Text {
            text: "General Settings"
            font.pixelSize: Theme.fontSizeMedium
            font.bold: true
            color: Theme.textPrimary
        }

        Row {
            spacing: 12
            Text {
                text: "Default Author:"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textPrimary
                width: 120
                anchors.verticalCenter: parent.verticalCenter
            }

            Rectangle {
                width: 260
                height: 28
                color: Theme.windowBackground
                border.color: Theme.borderSubtle
                border.width: 1
                radius: 3

                TextInput {
                    id: authorInput
                    anchors.fill: parent
                    anchors.margins: 4
                    text: settingsController.defaultAuthor
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeSmall
                }
            }
        }

        Row {
            spacing: 12
            Text {
                text: "Application Theme:"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textPrimary
                width: 120
                anchors.verticalCenter: parent.verticalCenter
            }

            Row {
                spacing: 8
                RadioButton {
                    text: "Light"
                    checked: appController.theme === "light"
                    onClicked: appController.setTheme("light")
                }
                RadioButton {
                    text: "Dark"
                    checked: appController.theme === "dark"
                    onClicked: appController.setTheme("dark")
                }
            }
        }

        Row {
            spacing: 12
            Text {
                text: "Autosave Interval:"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textPrimary
                width: 120
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: "Every 5 minutes"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.divider
        }

        Text {
            text: "OCR Engine (Tesseract)"
            font.pixelSize: Theme.fontSizeMedium
            font.bold: true
            color: Theme.textPrimary
        }

        Row {
            spacing: 12
            Text {
                text: "Tesseract Path:"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textPrimary
                width: 120
                anchors.verticalCenter: parent.verticalCenter
            }

            Rectangle {
                width: 260
                height: 28
                color: Theme.windowBackground
                border.color: Theme.borderSubtle
                border.width: 1
                radius: 3

                TextInput {
                    id: tessInput
                    anchors.fill: parent
                    anchors.margins: 4
                    text: settingsController.tesseractPath
                    placeholderText: "Auto-detected from PATH"
                    color: Theme.textPrimary
                    font.pixelSize: Theme.fontSizeSmall
                }
            }
        }

        Text {
            text: "Status: " + (ocrController.isTesseractAvailable ? "Tesseract found and ready." : "Tesseract not found in PATH.")
            font.pixelSize: Theme.fontSizeSmall
            color: ocrController.isTesseractAvailable ? Theme.statusSuccess : Theme.statusWarning
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.divider
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 12

            Button {
                text: "Save & Close"
                onClicked: {
                    settingsController.defaultAuthor = authorInput.text
                    settingsController.tesseractPath = tessInput.text
                    root.close()
                }
            }

            Button {
                text: "Cancel"
                onClicked: root.close()
            }
        }
    }
}
