import QtQuick
import QtQuick.Controls
import "../components"
import "../themes"

Dialog {
    id: root
    width: 400
    height: 240
    modal: true
    anchors.centerIn: parent

    property string targetFilePath: ""

    background: Rectangle {
        color: Theme.cardBackground
        border.color: Theme.borderSubtle
        border.width: 1
        radius: 6
    }

    Column {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 12

        Row {
            spacing: 8
            Text { text: "🔒"; font.pixelSize: 16 }
            Text {
                text: "Password Required"
                font.pixelSize: Theme.fontSizeMedium
                font.bold: true
                color: Theme.textPrimary
            }
        }

        Text {
            text: "This document is password protected. Please enter the password to open it:"
            font.pixelSize: Theme.fontSizeNormal
            color: Theme.textPrimary
            wrapMode: Text.WordWrap
            width: parent.width
        }

        Rectangle {
            width: parent.width
            height: 32
            radius: 4
            color: Theme.windowBackground
            border.color: passInput.activeFocus ? Theme.borderFocused : Theme.borderSubtle
            border.width: 1

            TextInput {
                id: passInput
                anchors.fill: parent
                anchors.margins: 6
                echoMode: TextInput.Password
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textPrimary
                onAccepted: root.submit()
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 12

            OqButton {
                text: "Unlock"
                isPrimary: true
                onClicked: root.submit()
            }

            OqButton {
                text: "Cancel"
                onClicked: root.close()
            }
        }
    }

    function submit() {
        if (passInput.text.length > 0) {
            pdfController.openDocument(root.targetFilePath, passInput.text)
            passInput.text = ""
            root.close()
        }
    }
}
