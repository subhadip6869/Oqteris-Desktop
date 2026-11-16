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
            text: "About Oqteris"
            iconSymbol: "ℹ"
            tooltipText: "Application Information and Credits"
            onClicked: aboutDialogLoader.openAboutDialog()
        }

        OqRibbonButton {
            text: "Settings"
            iconSymbol: "⚙"
            tooltipText: "Application Preferences"
            onClicked: settingsDialogLoader.openSettingsDialog()
        }

        OqRibbonButton {
            text: "Toggle Theme"
            iconSymbol: appController.isDarkMode ? "☀" : "🌙"
            tooltipText: "Switch Light / Dark Theme"
            onClicked: appController.toggleTheme()
        }
    }
}
