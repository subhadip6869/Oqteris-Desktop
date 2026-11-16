import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Item {
    id: root

    Column {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 10

        Row {
            width: parent.width
            Text {
                text: "Digital Signatures"
                font.pixelSize: Theme.fontSizeMedium
                font.weight: Font.DemiBold
                color: Theme.textPrimary
                anchors.verticalCenter: parent.verticalCenter
            }

            Item { width: 1; height: 1; Layout.fillWidth: true }

            Rectangle {
                width: 70
                height: 24
                radius: 3
                color: refreshMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                border.color: Theme.borderSubtle
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "Validate"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.brandPrimary
                }

                MouseArea {
                    id: refreshMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: signatureController.inspectSignatures()
                }
            }
        }

        ListView {
            width: parent.width
            height: parent.height - 40
            clip: true
            spacing: 8
            model: signatureController.documentSignatures

            delegate: Rectangle {
                width: parent.width
                height: 110
                color: Theme.cardBackground
                border.color: {
                    if (modelData.trustStatus === "trusted") return Theme.statusSuccess
                    if (modelData.trustStatus === "untrusted") return Theme.statusWarning
                    return Theme.statusError
                }
                border.width: 1.5
                radius: 4

                Column {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 4

                    Row {
                        spacing: 6
                        Text {
                            text: {
                                if (modelData.trustStatus === "trusted") return "✔"
                                if (modelData.trustStatus === "untrusted") return "⚠"
                                return "✖"
                            }
                            color: {
                                if (modelData.trustStatus === "trusted") return Theme.statusSuccess
                                if (modelData.trustStatus === "untrusted") return Theme.statusWarning
                                return Theme.statusError
                            }
                            font.pixelSize: 14
                            font.weight: Font.Bold
                        }

                        Text {
                            text: modelData.trustStatus.toUpperCase()
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: {
                                if (modelData.trustStatus === "trusted") return Theme.statusSuccess
                                if (modelData.trustStatus === "untrusted") return Theme.statusWarning
                                return Theme.statusError
                            }
                        }
                    }

                    Text {
                        text: "Signer: " + modelData.signerName
                        font.pixelSize: Theme.fontSizeSmall
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                        elide: Text.ElideRight
                        width: parent.width
                    }

                    Text {
                        text: "Crypto Valid: " + (modelData.isValid ? "Yes" : "No") + " | Intact: " + (modelData.isIntact ? "Yes" : "No")
                        font.pixelSize: 10
                        color: Theme.textSecondary
                    }

                    Text {
                        text: "Doc Modified: " + (modelData.docModified ? "Yes (Warning)" : "No")
                        font.pixelSize: 10
                        color: modelData.docModified ? Theme.statusWarning : Theme.textSecondary
                    }

                    Text {
                        text: modelData.validationMessage
                        font.pixelSize: 10
                        color: Theme.textSecondary
                        elide: Text.ElideRight
                        width: parent.width
                    }
                }
            }

            Text {
                anchors.centerIn: parent
                text: "No digital signatures found in this document"
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeNormal
                visible: signatureController.signatureCount === 0
            }
        }
    }
}
