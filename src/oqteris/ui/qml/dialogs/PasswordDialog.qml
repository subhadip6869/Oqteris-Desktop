import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Dialog {
    id: root
    title: "Password Required"
    width: 380
    height: 220
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
        anchors.margins: 16
        spacing: 12

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

            Button {
                text: "Unlock"
                onClicked: root.submit()
            }

            Button {
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
