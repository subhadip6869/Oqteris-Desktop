import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../themes"

Item {
    id: root

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Panel Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "Digital Signatures"
                font.pixelSize: Theme.fontSizeMedium
                font.weight: Font.DemiBold
                color: Theme.textPrimary
            }

            Rectangle {
                width: sigBadge.implicitWidth + 8
                height: 18
                radius: 9
                color: signatureController.signatureCount > 0
                    ? (signatureController.allValidAndTrusted ? Theme.statusSuccess : Theme.statusWarning)
                    : Theme.borderSubtle
                visible: signatureController.signatureCount > 0

                Text {
                    id: sigBadge
                    anchors.centerIn: parent
                    text: signatureController.signatureCount
                    font.pixelSize: 10
                    font.bold: true
                    color: "#FFFFFF"
                }
            }

            Item { Layout.fillWidth: true }

            // Validate Button
            Rectangle {
                Layout.preferredWidth: 68
                Layout.preferredHeight: 24
                radius: 3
                color: refreshMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                border.color: Theme.borderSubtle
                border.width: 1

                Row {
                    anchors.centerIn: parent
                    spacing: 4
                    Text { text: "🔄"; font.pixelSize: 10 }
                    Text {
                        text: "Validate"
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.brandPrimary
                        font.bold: true
                    }
                }

                MouseArea {
                    id: refreshMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: signatureController.inspectSignatures()
                }
            }

            // Import Certificate Button
            Rectangle {
                Layout.preferredWidth: 60
                Layout.preferredHeight: 24
                radius: 3
                color: importMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                border.color: Theme.borderSubtle
                border.width: 1

                Row {
                    anchors.centerIn: parent
                    spacing: 4
                    Text { text: "📥"; font.pixelSize: 10 }
                    Text {
                        text: "Import"
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textPrimary
                    }
                }

                MouseArea {
                    id: importMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: importCertDialog.open()
                }
            }
        }

        // Summary Banner (if document has signatures)
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: bannerCol.implicitHeight + 12
            radius: 4
            visible: signatureController.hasSignatures
            color: signatureController.allValidAndTrusted
                ? (appController.isDarkMode ? "#1B3320" : "#E8F5E9")
                : (appController.isDarkMode ? "#332B15" : "#FFF8E1")
            border.color: signatureController.allValidAndTrusted ? Theme.statusSuccess : Theme.statusWarning
            border.width: 1

            RowLayout {
                id: bannerCol
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8

                Text {
                    text: signatureController.allValidAndTrusted ? "✓" : "?"
                    font.pixelSize: 16
                    font.bold: true
                    color: signatureController.allValidAndTrusted ? Theme.statusSuccess : Theme.statusWarning
                }

                Text {
                    text: signatureController.allValidAndTrusted
                        ? "All signatures are verified and trusted."
                        : "Signatures detected: identity verification required."
                    font.pixelSize: Theme.fontSizeSmall
                    font.weight: Font.DemiBold
                    color: signatureController.allValidAndTrusted ? Theme.statusSuccess : Theme.statusWarning
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
            }
        }

        // Signatures List
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 10
            model: signatureController.documentSignatures

            delegate: Rectangle {
                width: ListView.view.width
                implicitHeight: cardLayout.implicitHeight + 16
                color: Theme.cardBackground
                radius: 6
                border.width: 1.5
                border.color: {
                    if (modelData.trustStatus === "trusted") return Theme.statusSuccess
                    if (modelData.trustStatus === "untrusted") return Theme.statusWarning
                    return Theme.statusError
                }

                ColumnLayout {
                    id: cardLayout
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    // Card Status Badge & Page
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        // Status Badge
                        Rectangle {
                            Layout.preferredHeight: 22
                            Layout.preferredWidth: badgeRow.implicitWidth + 12
                            radius: 11
                            color: {
                                if (modelData.trustStatus === "trusted") return Theme.statusSuccess
                                if (modelData.trustStatus === "untrusted") return Theme.statusWarning
                                return Theme.statusError
                            }

                            Row {
                                id: badgeRow
                                anchors.centerIn: parent
                                spacing: 4

                                Text {
                                    text: {
                                        if (modelData.trustStatus === "trusted") return "✓"
                                        if (modelData.trustStatus === "untrusted") return "?"
                                        return "✕"
                                    }
                                    color: "#FFFFFF"
                                    font.pixelSize: 11
                                    font.bold: true
                                }

                                Text {
                                    text: {
                                        if (modelData.trustStatus === "trusted") return "SIGNATURE VALID"
                                        if (modelData.trustStatus === "untrusted") return "SIGNATURE NOT VERIFIED"
                                        return "INVALID SIGNATURE"
                                    }
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: "#FFFFFF"
                                }
                            }
                        }

                        Item { Layout.fillWidth: true }

                        // Page Jump Button
                        Rectangle {
                            Layout.preferredHeight: 20
                            Layout.preferredWidth: pageJumpText.implicitWidth + 10
                            radius: 3
                            color: pageJumpMouse.containsMouse ? Theme.buttonHover : "transparent"
                            border.color: Theme.borderSubtle
                            border.width: 1

                            Text {
                                id: pageJumpText
                                anchors.centerIn: parent
                                text: "Page " + (modelData.pageNumber + 1)
                                font.pixelSize: 10
                                color: Theme.brandPrimary
                            }

                            MouseArea {
                                id: pageJumpMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: pdfController.currentPage = modelData.pageNumber
                            }
                        }
                    }

                    // Signer Name
                    Text {
                        text: modelData.signerName
                        font.pixelSize: Theme.fontSizeNormal
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    // Metadata Rows (Date, Reason, Location)
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: "📅 Date: " + (modelData.signingTime || "Not specified")
                            font.pixelSize: 11
                            color: Theme.textSecondary
                            visible: modelData.signingTime !== ""
                        }

                        Text {
                            text: "📝 Reason: " + modelData.reason
                            font.pixelSize: 11
                            color: Theme.textSecondary
                            visible: modelData.reason !== ""
                        }

                        Text {
                            text: "📍 Location: " + modelData.location
                            font.pixelSize: 11
                            color: Theme.textSecondary
                            visible: modelData.location !== ""
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: Theme.divider
                    }

                    // Verification Breakdown
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Row {
                            spacing: 4
                            Text {
                                text: modelData.docModified ? "✕" : "✓"
                                font.pixelSize: 11
                                font.bold: true
                                color: modelData.docModified ? Theme.statusError : Theme.statusSuccess
                            }
                            Text {
                                text: modelData.docModified ? "Document was modified after signing" : "Document has not been modified since signed"
                                font.pixelSize: 10
                                color: modelData.docModified ? Theme.statusError : Theme.textSecondary
                            }
                        }

                        Row {
                            spacing: 4
                            Text {
                                text: modelData.trustStatus === "trusted" ? "✓" : "⚠"
                                font.pixelSize: 11
                                font.bold: true
                                color: modelData.trustStatus === "trusted" ? Theme.statusSuccess : Theme.statusWarning
                            }
                            Text {
                                text: modelData.trustStatus === "trusted" ? "Signer's identity is trusted" : "Signer's certificate is not in your trusted list"
                                font.pixelSize: 10
                                color: modelData.trustStatus === "trusted" ? Theme.statusSuccess : Theme.statusWarning
                            }
                        }
                    }

                    // Action Buttons Row
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.topMargin: 4
                        spacing: 6

                        // Trust / Untrust Button
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 28
                            radius: 4
                            color: modelData.trustStatus === "trusted"
                                ? (cardTrustMouse.containsMouse ? Theme.buttonHover : "transparent")
                                : (cardTrustMouse.containsMouse ? Theme.brandPrimaryHover : Theme.brandPrimary)
                            border.color: modelData.trustStatus === "trusted" ? Theme.borderSubtle : "transparent"
                            border.width: 1

                            Row {
                                anchors.centerIn: parent
                                spacing: 4
                                Text {
                                    text: modelData.trustStatus === "trusted" ? "✖" : "🛡"
                                    font.pixelSize: 11
                                    color: modelData.trustStatus === "trusted" ? Theme.statusError : "#FFFFFF"
                                }
                                Text {
                                    text: modelData.trustStatus === "trusted" ? "Remove Trust" : "Trust Certificate"
                                    font.pixelSize: Theme.fontSizeSmall
                                    font.bold: true
                                    color: modelData.trustStatus === "trusted" ? Theme.statusError : "#FFFFFF"
                                }
                            }

                            MouseArea {
                                id: cardTrustMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (modelData.trustStatus === "trusted") {
                                        signatureController.untrustSignatureCertificate(index)
                                    } else {
                                        signatureController.trustSignatureCertificate(index)
                                    }
                                }
                            }
                        }

                        // Certificate Details Button
                        Rectangle {
                            Layout.preferredWidth: 64
                            Layout.preferredHeight: 28
                            radius: 4
                            color: detMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                            border.color: Theme.borderSubtle
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "Details..."
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.brandPrimary
                            }

                            MouseArea {
                                id: detMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: certDetailsDialogLoader.openCertificateDialog(index)
                            }
                        }
                    }
                }
            }

            // Empty State
            Item {
                anchors.fill: parent
                visible: signatureController.signatureCount === 0

                Column {
                    anchors.centerIn: parent
                    spacing: 12
                    width: parent.width - 40

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "🔏"
                        font.pixelSize: 36
                    }

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "No Digital Signatures Found"
                        font.pixelSize: Theme.fontSizeMedium
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                    }

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "This document does not contain cryptographic signatures. You can sign this PDF using the 'Fill & Sign' or 'Protect' tab."
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textSecondary
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }
                }
            }
        }
    }
}
