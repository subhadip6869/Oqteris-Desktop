import QtQuick

pragma Singleton

QtObject {
    id: themeRoot

    // Determine current mode from appController
    readonly property bool isDark: (typeof appController !== "undefined" && appController) ? appController.isDarkMode : false

    // Brand Colors
    readonly property color brandPrimary: "#0078D4"
    readonly property color brandSecondary: "#00B4D8"
    readonly property color brandAccent: "#0096C7"
    readonly property color brandHover: "#106EBE"

    // Background & Surface
    readonly property color windowBackground: isDark ? "#1E1E1E" : "#F3F3F3"
    readonly property color workspaceBackground: isDark ? "#181818" : "#E5E5E5"
    readonly property color ribbonBackground: isDark ? "#252526" : "#FBFBFB"
    readonly property color cardBackground: isDark ? "#2D2D30" : "#FFFFFF"
    readonly property color panelBackground: isDark ? "#252526" : "#F7F7F7"
    readonly property color titleBarBackground: isDark ? "#1F1F1F" : "#F0F0F0"

    // Borders & Dividers
    readonly property color borderSubtle: isDark ? "#3E3E42" : "#E0E0E0"
    readonly property color borderFocused: brandPrimary
    readonly property color divider: isDark ? "#333337" : "#EAEAEA"

    // Typography
    readonly property color textPrimary: isDark ? "#F1F1F1" : "#1A1A1A"
    readonly property color textSecondary: isDark ? "#AAAAAA" : "#616161"
    readonly property color textDisabled: isDark ? "#666666" : "#9E9E9E"
    readonly property color textOnBrand: "#FFFFFF"

    // Interactive States
    readonly property color buttonHover: isDark ? "#3E3E42" : "#ECECEC"
    readonly property color buttonPressed: isDark ? "#4E4E52" : "#DFDFDF"
    readonly property color selectedBackground: isDark ? "#094771" : "#E1EBF5"
    readonly property color activeTabIndicator: brandPrimary

    // Status Colors
    readonly property color statusSuccess: "#107C41"
    readonly property color statusWarning: "#D83B01"
    readonly property color statusError: "#A80000"
    readonly property color statusInfo: brandPrimary

    // Fonts
    readonly property string fontFamily: "Segoe UI, sans-serif"
    readonly property int fontSizeSmall: 11
    readonly property int fontSizeNormal: 12
    readonly property int fontSizeMedium: 14
    readonly property int fontSizeLarge: 16
    readonly property int fontSizeTitle: 20
}
