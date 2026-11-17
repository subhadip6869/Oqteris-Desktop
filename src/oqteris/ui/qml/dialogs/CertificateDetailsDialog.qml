import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Window
import "../components"
import "../themes"

Window {
    id: root
    title: "Certificate Information"
    width: 560
    height: 520
    minimumWidth: 460
    minimumHeight: 380
    modality: Qt.ApplicationModal
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
    color: Theme.windowBackground

    property int signatureIndex: 0
    property var certData: ({})

    function openForSignature(index) {
        signatureIndex = index
        certData = signatureController.getCertificateDetails(index)
        root.show()
        root.raise()
        root.requestActivate()
    }

    function open() {
        root.show()
        root.raise()
        root.requestActivate()
    }

    function close() {
        root.hide()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // Status Header Card
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            radius: 5
            color: certData.isTrusted ? (appController.isDarkMode ? "#1B3320" : "#E8F5E9")
                                      : (appController.isDarkMode ? "#332B15" : "#FFF8E1")
            border.color: certData.isTrusted ? Theme.statusSuccess : Theme.statusWarning
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                Rectangle {
                    width: 36
                    height: 36
                    radius: 18
                    color: certData.isTrusted ? Theme.statusSuccess : Theme.statusWarning

                    Text {
                        anchors.centerIn: parent
                        text: certData.isTrusted ? "✓" : "?"
                        font.pixelSize: 18
                        font.bold: true
                        color: "#FFFFFF"
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: certData.isTrusted ? "Trusted Certificate" : "Certificate Not Trusted"
                        font.pixelSize: Theme.fontSizeMedium
                        font.bold: true
                        color: certData.isTrusted ? Theme.statusSuccess : Theme.statusWarning
                    }

                    Text {
                        text: certData.isTrusted
                            ? "This certificate was verified and is marked as trusted."
                            : "The identity of the signer has not been verified against your trusted roots."
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textSecondary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                }
            }
        }

        // Detailed Certificate Information View
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: parent.width
                spacing: 10

                // Section 1: Subject / Signer
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: colSubject.implicitHeight + 16
                    color: Theme.cardBackground
                    radius: 4
                    border.color: Theme.borderSubtle
                    border.width: 1

                    ColumnLayout {
                        id: colSubject
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 4

                        Text {
                            text: "ISSUED TO (SIGNER)"
                            font.pixelSize: 10
                            font.bold: true
                            color: Theme.brandPrimary
                        }

                        Text {
                            text: "Common Name: " + (certData.commonName || "Unknown")
                            font.pixelSize: Theme.fontSizeNormal
                            font.weight: Font.DemiBold
                            color: Theme.textPrimary
                        }

                        Text {
                            text: "Organization: " + (certData.organization || "None specified")
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textSecondary
                            visible: certData.organization !== undefined
                        }
                    }
                }

                // Section 2: Issuer (CA)
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: colIssuer.implicitHeight + 16
                    color: Theme.cardBackground
                    radius: 4
                    border.color: Theme.borderSubtle
                    border.width: 1

                    ColumnLayout {
                        id: colIssuer
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 4

                        Text {
                            text: "ISSUED BY (AUTHORITY)"
                            font.pixelSize: 10
                            font.bold: true
                            color: Theme.brandPrimary
                        }

                        Text {
                            text: "Issuer: " + (certData.issuer || "Self-signed")
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textPrimary
                        }

                        Text {
                            text: "Self-Signed Certificate: " + (certData.isSelfSigned ? "Yes" : "No")
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textSecondary
                        }
                    }
                }

                // Section 3: Validity Period
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: colValidity.implicitHeight + 16
                    color: Theme.cardBackground
                    radius: 4
                    border.color: Theme.borderSubtle
                    border.width: 1

                    ColumnLayout {
                        id: colValidity
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 4

                        Text {
                            text: "VALIDITY PERIOD"
                            font.pixelSize: 10
                            font.bold: true
                            color: Theme.brandPrimary
                        }

                        Text {
                            text: "Valid From: " + (certData.validFrom || "N/A")
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textPrimary
                        }

                        Text {
                            text: "Valid Until: " + (certData.validTo || "N/A")
                            font.pixelSize: Theme.fontSizeSmall
                            color: certData.isExpired ? Theme.statusError : Theme.textPrimary
                        }
                    }
                }

                // Section 4: Cryptographic Fingerprint & Serial
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: colCrypto.implicitHeight + 16
                    color: Theme.cardBackground
                    radius: 4
                    border.color: Theme.borderSubtle
                    border.width: 1

                    ColumnLayout {
                        id: colCrypto
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 4

                        Text {
                            text: "CRYPTOGRAPHIC FINGERPRINT"
                            font.pixelSize: 10
                            font.bold: true
                            color: Theme.brandPrimary
                        }

                        Text {
                            text: "SHA-256: " + (certData.fingerprintSha256 || "N/A")
                            font.pixelSize: 10
                            font.family: "Consolas, monospace"
                            color: Theme.textSecondary
                            wrapMode: Text.WrapAnywhere
                            Layout.fillWidth: true
                        }

                        Text {
                            text: "Serial Number: " + (certData.serialNumber || "N/A")
                            font.pixelSize: 10
                            font.family: "Consolas, monospace"
                            color: Theme.textSecondary
                        }
                    }
                }
            }
        }

        // Bottom Action Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            // Trust / Untrust Button
            Rectangle {
                Layout.preferredWidth: btnTrustText.implicitWidth + 24
                Layout.preferredHeight: 32
                radius: 4
                color: certData.isTrusted ? Theme.buttonHover : Theme.brandPrimary

                Text {
                    id: btnTrustText
                    anchors.centerIn: parent
                    text: certData.isTrusted ? "Remove Trust" : "Trust Certificate"
                    font.pixelSize: Theme.fontSizeSmall
                    font.bold: true
                    color: certData.isTrusted ? Theme.statusError : "#FFFFFF"
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (certData.isTrusted) {
                            signatureController.untrustSignatureCertificate(root.signatureIndex)
                        } else {
                            signatureController.trustSignatureCertificate(root.signatureIndex)
                        }
                        // Refresh data
                        root.certData = signatureController.getCertificateDetails(root.signatureIndex)
                    }
                }
            }

            // Export Certificate Button
            Rectangle {
                Layout.preferredWidth: btnExportText.implicitWidth + 20
                Layout.preferredHeight: 32
                radius: 4
                color: expMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                border.color: Theme.borderSubtle
                border.width: 1

                Text {
                    id: btnExportText
                    anchors.centerIn: parent
                    text: "Export Public Cert..."
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textPrimary
                }

                MouseArea {
                    id: expMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        exportCertDialog.targetSigIndex = root.signatureIndex
                        exportCertDialog.open()
                    }
                }
            }

            Item { Layout.fillWidth: true }

            // Close Button
            Rectangle {
                Layout.preferredWidth: 70
                Layout.preferredHeight: 32
                radius: 4
                color: closeMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                border.color: Theme.borderSubtle
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "Close"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textPrimary
                }

                MouseArea {
                    id: closeMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.close()
                }
            }
        }
    }
}
