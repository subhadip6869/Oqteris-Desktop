import QtQuick
import QtQuick.Controls
import "../components"
import "../themes"

Dialog {
    id: root
    width: 520
    height: 440
    modal: true
    anchors.centerIn: parent

    background: Rectangle {
        color: Theme.cardBackground
        border.color: Theme.borderSubtle
        border.width: 1
        radius: 6
    }

    onAboutToShow: {
        if (updateController.status === "idle" || updateController.status === "error") {
            updateController.checkForUpdates()
        }
    }

    function openAndCheck() {
        open()
        updateController.checkForUpdates()
    }

    function formatBytes(bytes) {
        if (!bytes || bytes <= 0) return "0 B"
        var k = 1024
        var sizes = ["B", "KB", "MB", "GB"]
        var i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i]
    }

    Column {
        anchors.fill: parent
        spacing: 0

        // ── Title Header ──────────────────────────────────────────────────
        Rectangle {
            width: parent.width
            height: 44
            color: Theme.panelBackground
            radius: 6

            // Clip bottom corners square
            Rectangle {
                width: parent.width
                height: parent.height / 2
                anchors.bottom: parent.bottom
                color: parent.color
            }

            Item {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16

                Row {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 10

                    OqIcon {
                        anchors.verticalCenter: parent.verticalCenter
                        name: "update"
                        size: 18
                        color: Theme.brandPrimary
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Software Update"
                        font.pixelSize: Theme.fontSizeLarge
                        font.weight: Font.DemiBold
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }
                }

                // Close button (cross icon)
                Rectangle {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    width: 28
                    height: 28
                    radius: 4
                    color: closeArea.containsMouse ? Theme.buttonHover : "transparent"

                    OqIcon {
                        anchors.centerIn: parent
                        name: "close"
                        size: 14
                        color: closeArea.containsMouse ? Theme.textPrimary : Theme.textSecondary
                    }

                    MouseArea {
                        id: closeArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.close()
                    }
                }
            }

            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        // ── Central Body Area ─────────────────────────────────────────────
        Item {
            width: parent.width
            height: parent.height - 44

            // ── State 1: Checking for updates ─────────────────────────────
            Column {
                anchors.centerIn: parent
                spacing: 16
                visible: updateController.status === "checking" || updateController.status === "idle"

                // Rotating circular update icon
                Rectangle {
                    width: 48
                    height: 48
                    radius: 24
                    color: Theme.inputBackground
                    border.color: Theme.brandPrimary
                    border.width: 1.5
                    anchors.horizontalCenter: parent.horizontalCenter

                    OqIcon {
                        anchors.centerIn: parent
                        name: "update"
                        size: 24
                        color: Theme.brandPrimary
                        transformOrigin: Item.Center

                        RotationAnimation on rotation {
                            from: 0
                            to: 360
                            duration: 1200
                            loops: Animation.Infinite
                            running: updateController.status === "checking"
                        }
                    }
                }

                Column {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 4

                    Text {
                        text: "Checking for updates..."
                        font.pixelSize: Theme.fontSizeMedium
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "Connecting to GitHub Releases for " + appController.appName + "..."
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            // ── State 2: Up to date ────────────────────────────────────────
            Column {
                anchors.centerIn: parent
                spacing: 16
                visible: updateController.status === "up_to_date"

                Rectangle {
                    width: 56
                    height: 56
                    radius: 28
                    color: Theme.isDark ? "#143825" : "#E6F4EA"
                    border.color: Theme.statusSuccess
                    border.width: 1.5
                    anchors.horizontalCenter: parent.horizontalCenter

                    OqIcon {
                        anchors.centerIn: parent
                        name: "check"
                        size: 28
                        color: Theme.statusSuccess
                    }
                }

                Column {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 6

                    Text {
                        text: "You're up to date!"
                        font.pixelSize: Theme.fontSizeTitle
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: appController.appName + " v" + appController.appVersion + " is currently the newest version available."
                        font.pixelSize: Theme.fontSizeNormal
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "Running on " + appController.osName
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textDisabled
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 10
                    topPadding: 8

                    OqButton {
                        text: "Check Again"
                        iconName: "update"
                        onClicked: updateController.checkForUpdates()
                    }

                    OqButton {
                        text: "Close"
                        isPrimary: true
                        onClicked: root.close()
                    }
                }
            }

            // ── State 3: Update Available ──────────────────────────────────
            Column {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 12
                visible: updateController.status === "available"

                Row {
                    width: parent.width
                    spacing: 10

                    Rectangle {
                        width: 36
                        height: 36
                        radius: 18
                        color: Theme.isDark ? "#1C3550" : "#E0F2FE"
                        border.color: Theme.brandPrimary
                        border.width: 1

                        OqIcon {
                            anchors.centerIn: parent
                            name: "sparkles"
                            size: 20
                            color: Theme.brandPrimary
                        }
                    }

                    Column {
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 2
                        width: parent.width - 50

                        Row {
                            spacing: 8
                            Text {
                                text: "New Version Available!"
                                font.pixelSize: Theme.fontSizeMedium
                                font.bold: true
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                            }

                            Rectangle {
                                width: vTag.implicitWidth + 10
                                height: 18
                                radius: 3
                                color: Theme.brandPrimary
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    id: vTag
                                    anchors.centerIn: parent
                                    text: "v" + updateController.latestVersion
                                    font.pixelSize: 11
                                    font.bold: true
                                    font.family: Theme.fontFamily
                                    color: "#FFFFFF"
                                }
                            }
                        }

                        Text {
                            text: "Current: v" + appController.appVersion +
                                  (updateController.releaseDate ? "  ·  Released: " + updateController.releaseDate : "") +
                                  (updateController.assetSizeFormatted ? "  ·  Size: " + updateController.assetSizeFormatted : "")
                            font.pixelSize: Theme.fontSizeSmall
                            font.family: Theme.fontFamily
                            color: Theme.textSecondary
                        }
                    }
                }

                // Release notes container
                Column {
                    width: parent.width
                    spacing: 4

                    Text {
                        text: "Release Notes:"
                        font.pixelSize: Theme.fontSizeSmall
                        font.weight: Font.DemiBold
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                    }

                    Rectangle {
                        width: parent.width
                        height: 200
                        color: Theme.inputBackground
                        border.color: Theme.borderSubtle
                        border.width: 1
                        radius: 4

                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 10
                            clip: true

                            Text {
                                width: parent.width - 16
                                text: updateController.releaseNotes || "Bug fixes and performance improvements."
                                font.pixelSize: Theme.fontSizeSmall
                                font.family: Theme.fontFamily
                                color: Theme.textPrimary
                                wrapMode: Text.Wrap
                            }
                        }
                    }
                }

                // Action buttons
                Row {
                    anchors.right: parent.right
                    spacing: 8
                    topPadding: 4

                    OqButton {
                        text: "View on GitHub"
                        onClicked: updateController.openReleasePage()
                    }

                    OqButton {
                        text: "Later"
                        onClicked: root.close()
                    }

                    OqButton {
                        text: "Download & Install"
                        isPrimary: true
                        iconName: "download"
                        onClicked: updateController.startDownload()
                    }
                }
            }

            // ── State 4: Downloading ───────────────────────────────────────
            Column {
                anchors.centerIn: parent
                width: parent.width - 48
                spacing: 16
                visible: updateController.status === "downloading"

                Rectangle {
                    width: 52
                    height: 52
                    radius: 26
                    color: Theme.isDark ? "#1C3550" : "#E0F2FE"
                    border.color: Theme.brandPrimary
                    border.width: 1.5
                    anchors.horizontalCenter: parent.horizontalCenter

                    OqIcon {
                        anchors.centerIn: parent
                        name: "download"
                        size: 24
                        color: Theme.brandPrimary
                    }
                }

                Column {
                    width: parent.width
                    spacing: 4

                    Text {
                        text: "Downloading Oqteris v" + updateController.latestVersion + "..."
                        font.pixelSize: Theme.fontSizeMedium
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: updateController.assetName
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        elide: Text.ElideMiddle
                        width: Math.min(parent.width, 360)
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }

                // Progress Bar
                Column {
                    width: parent.width
                    spacing: 6

                    Rectangle {
                        width: parent.width
                        height: 12
                        radius: 6
                        color: Theme.inputBackground
                        border.color: Theme.borderSubtle
                        border.width: 1
                        clip: true

                        Rectangle {
                            height: parent.height
                            width: Math.max(6, parent.width * Math.min(1.0, Math.max(0.0, updateController.downloadProgress)))
                            radius: 6
                            color: Theme.brandPrimary

                            Behavior on width {
                                NumberAnimation { duration: 120 }
                            }
                        }
                    }

                    // Progress stats row
                    Item {
                        width: parent.width
                        height: 18

                        Text {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            text: Math.round(updateController.downloadProgress * 100) + "%  (" +
                                  root.formatBytes(updateController.downloadedBytes) + " / " +
                                  (updateController.totalBytes > 0 ? root.formatBytes(updateController.totalBytes) : "...") + ")"
                            font.pixelSize: Theme.fontSizeSmall
                            font.family: Theme.fontFamily
                            color: Theme.textSecondary
                        }

                        Text {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            text: updateController.downloadSpeed
                            font.pixelSize: Theme.fontSizeSmall
                            font.bold: true
                            font.family: Theme.fontFamily
                            color: Theme.brandPrimary
                        }
                    }
                }

                OqButton {
                    text: "Cancel Download"
                    anchors.horizontalCenter: parent.horizontalCenter
                    onClicked: updateController.cancelDownload()
                }
            }

            // ── State 5: Ready to Install ───────────────────────────────────
            Column {
                anchors.centerIn: parent
                spacing: 16
                visible: updateController.status === "ready_to_install"

                Rectangle {
                    width: 56
                    height: 56
                    radius: 28
                    color: Theme.isDark ? "#143825" : "#E6F4EA"
                    border.color: Theme.statusSuccess
                    border.width: 1.5
                    anchors.horizontalCenter: parent.horizontalCenter

                    OqIcon {
                        anchors.centerIn: parent
                        name: "check"
                        size: 28
                        color: Theme.statusSuccess
                    }
                }

                Column {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 6

                    Text {
                        text: "Update Ready to Install!"
                        font.pixelSize: Theme.fontSizeTitle
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "Oqteris v" + updateController.latestVersion + " has been downloaded successfully."
                        font.pixelSize: Theme.fontSizeNormal
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "Clicking 'Install & Restart' will launch the installer and exit Oqteris."
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textDisabled
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 10
                    topPadding: 8

                    OqButton {
                        text: "Install Later"
                        onClicked: root.close()
                    }

                    OqButton {
                        text: "Install & Restart"
                        isPrimary: true
                        onClicked: updateController.installUpdate()
                    }
                }
            }

            // ── State 6: Error ─────────────────────────────────────────────
            Column {
                anchors.centerIn: parent
                width: parent.width - 48
                spacing: 16
                visible: updateController.status === "error"

                Rectangle {
                    width: 56
                    height: 56
                    radius: 28
                    color: Theme.isDark ? "#381A1A" : "#FEE2E2"
                    border.color: Theme.statusError
                    border.width: 1.5
                    anchors.horizontalCenter: parent.horizontalCenter

                    OqIcon {
                        anchors.centerIn: parent
                        name: "alert-circle"
                        size: 28
                        color: Theme.statusError
                    }
                }

                Column {
                    width: parent.width
                    spacing: 6

                    Text {
                        text: "Update Error"
                        font.pixelSize: Theme.fontSizeTitle
                        font.bold: true
                        font.family: Theme.fontFamily
                        color: Theme.statusError
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: updateController.errorMessage || "An error occurred while communicating with the update server."
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        wrapMode: Text.Wrap
                        width: parent.width - 32
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 10
                    topPadding: 6

                    OqButton {
                        text: "Try Again"
                        isPrimary: true
                        iconName: "update"
                        onClicked: updateController.checkForUpdates()
                    }

                    OqButton {
                        text: "View on GitHub"
                        onClicked: updateController.openReleasePage()
                    }

                    OqButton {
                        text: "Close"
                        onClicked: root.close()
                    }
                }
            }

        }  // Central Body Area
    }  // root Column
}  // Dialog
