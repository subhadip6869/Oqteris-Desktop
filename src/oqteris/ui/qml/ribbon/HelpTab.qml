import QtQuick
import "../components"
import "../themes"

Row {
    id: root
    spacing: 0
    height: 88

    // Group 1: Application Information
    OqRibbonGroup {
        title: "About"

        OqRibbonButton {
            text: "About\nOqteris"
            iconName: "properties"
            tooltipText: "Application Information and Credits"
            onClicked: aboutDialogLoader.openAboutDialog()
        }

        OqRibbonButton {
            text: "Check for\nUpdates"
            iconName: "update"
            tooltipText: "Check for the latest version from GitHub"
            onClicked: updateDialogLoader.openUpdateDialog()
        }

        OqRibbonButton {
            text: "Settings"
            iconName: "settings"
            tooltipText: "Application Preferences"
            onClicked: settingsDialogLoader.openSettingsDialog()
        }
    }
}
