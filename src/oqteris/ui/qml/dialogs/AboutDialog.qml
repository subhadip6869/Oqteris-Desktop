import QtQuick
import QtQuick.Controls
import "../components"
import "../themes"

Dialog {
    id: root
    width: 440
    height: 380
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

        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 4

            Text {
                text: appController.appName
                font.pixelSize: 24
                font.bold: true
                color: Theme.brandPrimary
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Version " + appController.appVersion
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: appController.appDescription
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textPrimary
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.divider
        }

        Column {
            width: parent.width
            spacing: 8

            Row {
                spacing: 8
                Text { text: "Organization:"; font.bold: true; font.pixelSize: Theme.fontSizeSmall; color: Theme.textPrimary; width: 100 }
                Text { text: appController.organizationName; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
            }

            Row {
                spacing: 8
                Text { text: "Developer:"; font.bold: true; font.pixelSize: Theme.fontSizeSmall; color: Theme.textPrimary; width: 100 }
                Text { text: appController.developerName; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
            }

            Row {
                spacing: 8
                Text { text: "Website:"; font.bold: true; font.pixelSize: Theme.fontSizeSmall; color: Theme.textPrimary; width: 100 }
                Text { text: appController.organizationUrl; font.pixelSize: Theme.fontSizeSmall; color: Theme.brandPrimary }
            }

            Row {
                spacing: 8
                Text { text: "Repository:"; font.bold: true; font.pixelSize: Theme.fontSizeSmall; color: Theme.textPrimary; width: 100 }
                Text { text: appController.repositoryUrl; font.pixelSize: Theme.fontSizeSmall; color: Theme.brandPrimary; elide: Text.ElideRight; width: 280 }
            }

            Row {
                spacing: 8
                Text { text: "Platform:"; font.bold: true; font.pixelSize: Theme.fontSizeSmall; color: Theme.textPrimary; width: 100 }
                Text { text: appController.osName + " (PySide6 / Qt Quick)"; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Theme.divider
        }

        Text {
            text: "Copyright © 2026 OriginSD / Subhadip Dutta. Apache License 2.0."
            font.pixelSize: 10
            color: Theme.textSecondary
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 12

            OqButton {
                text: "Check for Updates"
                onClicked: {
                    root.close()
                    updateDialogLoader.openUpdateDialog()
                }
            }

            OqButton {
                text: "Close"
                isPrimary: true
                onClicked: root.close()
            }
        }
    }
}
