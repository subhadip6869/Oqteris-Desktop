import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Dialog {
    id: root
    title: "Digital Signature"
    width: 480
    height: 440
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
            text: "Sign PDF with PKCS#12 (.p12 / .pfx) Certificate"
            font.pixelSize: Theme.fontSizeNormal
            font.weight: Font.DemiBold
            color: Theme.textPrimary
        }

        Column {
            width: parent.width
            spacing: 4
            Text { text: "Certificate File (.p12 / .pfx):"; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
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
                        id: certPathInput
                        anchors.fill: parent
                        anchors.margins: 4
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textPrimary
                    }
                }
                Button {
                    text: "Browse"
                    height: 28
                    onClicked: fileDialogLoader.openCertificate()
                }
            }
        }

        Column {
            width: parent.width
            spacing: 4
            Text { text: "Certificate Password / PIN:"; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
            Rectangle {
                width: parent.width
                height: 28
                color: Theme.windowBackground
                border.color: Theme.borderSubtle
                border.width: 1
                radius: 3
                TextInput {
                    id: pinInput
                    anchors.fill: parent
                    anchors.margins: 4
                    echoMode: TextInput.Password
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textPrimary
                }
            }
        }

        Column {
            width: parent.width
            spacing: 4
            Text { text: "Signing Reason:"; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
            Rectangle {
                width: parent.width
                height: 28
                color: Theme.windowBackground
                border.color: Theme.borderSubtle
                border.width: 1
                radius: 3
                TextInput {
                    id: reasonInput
                    anchors.fill: parent
                    anchors.margins: 4
                    text: "I approve and verify this document"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textPrimary
                }
            }
        }

        Column {
            width: parent.width
            spacing: 4
            Text { text: "Save Signed PDF As:"; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
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
                        id: outPathInput
                        anchors.fill: parent
                        anchors.margins: 4
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textPrimary
                    }
                }
                Button {
                    text: "Browse"
                    height: 28
                    onClicked: fileDialogLoader.saveSignedFileAs()
                }
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 12

            Button {
                text: "Sign Document"
                onClicked: {
                    if (certPathInput.text && outPathInput.text) {
                        signatureController.signDocument(
                            outPathInput.text,
                            certPathInput.text,
                            pinInput.text,
                            reasonInput.text,
                            "Oqteris Desktop",
                            pdfController.currentPage,
                            [50, 50, 250, 120]
                        )
                        root.close()
                    }
                }
            }

            Button {
                text: "Cancel"
                onClicked: root.close()
            }
        }
    }

    function setCertPath(path) { certPathInput.text = path }
    function setOutPath(path) { outPathInput.text = path }
}
