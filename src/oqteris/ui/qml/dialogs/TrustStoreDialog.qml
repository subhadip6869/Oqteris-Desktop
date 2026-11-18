import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../themes"

Dialog {
    id: root
    title: "Security & Trust Store"
    width: 560
    height: 480
    modal: true
    anchors.centerIn: parent

    background: Rectangle {
        color: Theme.cardBackground
        border.color: Theme.borderSubtle
        border.width: 1
        radius: 8
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 14

        // Header Card
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            radius: 6
            color: appController.isDarkMode ? "#1B3320" : "#E8F5E9"
            border.color: Theme.statusSuccess
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                Rectangle {
                    width: 36
                    height: 36
                    radius: 18
                    color: Theme.statusSuccess

                    Text {
                        anchors.centerIn: parent
                        text: "🛡"
                        font.pixelSize: 18
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: "Security & Trust Store"
                        font.pixelSize: Theme.fontSizeMedium
                        font.bold: true
                        color: appController.isDarkMode ? "#A5D6A7" : "#1B5E20"
                    }

                    Text {
                        text: "Manage trusted certificates and verification levels for digital signatures."
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textSecondary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                }
            }
        }

        // Section Title
        Text {
            text: "Trusted Certificates (" + (signatureController.trustedCertificates ? signatureController.trustedCertificates.length : 0) + ")"
            font.pixelSize: Theme.fontSizeNormal
            font.bold: true
            color: Theme.textPrimary
        }

        // Certificate List
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.windowBackground
            border.color: Theme.borderSubtle
            border.width: 1
            radius: 6
            clip: true

            ListView {
                id: certListView
                anchors.fill: parent
                anchors.margins: 6
                spacing: 6
                model: signatureController.trustedCertificates

                delegate: Rectangle {
                    width: certListView.width
                    height: 52
                    radius: 4
                    color: Theme.cardBackground
                    border.color: Theme.borderSubtle
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 10

                        Text {
                            text: "📜"
                            font.pixelSize: 16
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: modelData.commonName || modelData.subject || "Unnamed Certificate"
                                font.pixelSize: Theme.fontSizeSmall
                                font.bold: true
                                color: Theme.textPrimary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }

                            Text {
                                text: (modelData.issuer ? ("Issuer: " + modelData.issuer) : "") +
                                      (modelData.validTo ? (" • Valid to: " + modelData.validTo) : "")
                                font.pixelSize: 10
                                color: Theme.textSecondary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }

                        Button {
                            text: "Remove"
                            Layout.preferredHeight: 26
                            onClicked: {
                                if (modelData.id) {
                                    signatureController.removeCertificate(modelData.id)
                                }
                            }
                        }
                    }
                }

                // Empty State
                Item {
                    anchors.centerIn: parent
                    visible: !signatureController.trustedCertificates || signatureController.trustedCertificates.length === 0
                    width: parent.width - 40
                    height: 80

                    Column {
                        anchors.centerIn: parent
                        spacing: 6

                        Text {
                            text: "No trusted root certificates installed."
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textSecondary
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: "Click 'Import Certificate' below to add a trusted root or CA certificate."
                            font.pixelSize: 10
                            color: Theme.textDisabled
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }
        }

        // Dialog Footer Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "Import Certificate..."
                onClicked: {
                    fileDialogLoader.openCertificate()
                }
            }

            Item { Layout.fillWidth: true }

            Button {
                text: "Close"
                highlighted: true
                onClicked: root.close()
            }
        }
    }
}
