import QtQuick

pragma Singleton

QtObject {
    id: themeRoot

    // Determine current mode from appController
    readonly property bool isDark: (typeof appController !== "undefined" && appController) ? appController.isDarkMode : false

    // Brand Colors
    readonly property color brandPrimary: isDark ? "#4CC2FF" : "#0078D4"
    readonly property color brandSecondary: isDark ? "#70D4FF" : "#00B4D8"
    readonly property color brandAccent: isDark ? "#38B6FF" : "#0096C7"
    readonly property color brandHover: isDark ? "#6CD6FF" : "#106EBE"
    readonly property color brandPressed: isDark ? "#3098CC" : "#005A9E"

    // Background & Surface
    readonly property color windowBackground: isDark ? "#202020" : "#F3F3F3"
    readonly property color workspaceBackground: isDark ? "#181818" : "#E5E5E5"
    readonly property color ribbonBackground: isDark ? "#262626" : "#FFFFFF"
    readonly property color cardBackground: isDark ? "#2D2D2D" : "#FFFFFF"
    readonly property color panelBackground: isDark ? "#242424" : "#F8F8F8"
    readonly property color titleBarBackground: isDark ? "#202020" : "#F3F3F3"
    readonly property color inputBackground: isDark ? "#1C1C1C" : "#FFFFFF"

    // Borders & Dividers
    readonly property color borderSubtle: isDark ? "#3C3C3C" : "#DCDCDC"
    readonly property color borderFocused: brandPrimary
    readonly property color divider: isDark ? "#333333" : "#E5E5E5"

    // Typography
    readonly property color textPrimary: isDark ? "#F3F3F3" : "#1A1A1A"
    readonly property color textSecondary: isDark ? "#A0A0A0" : "#606060"
    readonly property color textDisabled: isDark ? "#666666" : "#A0A0A0"
    readonly property color textOnBrand: "#FFFFFF"

    // Interactive States
    readonly property color buttonHover: isDark ? "#383838" : "#EBEBEB"
    readonly property color buttonPressed: isDark ? "#484848" : "#DFDFDF"
    readonly property color selectedBackground: isDark ? "#1E3A5F" : "#E1EBF5"
    readonly property color activeTabIndicator: brandPrimary

    // Status Colors
    readonly property color statusSuccess: isDark ? "#34D399" : "#107C41"
    readonly property color statusWarning: isDark ? "#FBBF24" : "#D83B01"
    readonly property color statusError: isDark ? "#F87171" : "#A80000"
    readonly property color statusInfo: brandPrimary

    // Fonts
    readonly property string fontFamily: "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif"
    readonly property int fontSizeSmall: 11
    readonly property int fontSizeNormal: 12
    readonly property int fontSizeMedium: 14
    readonly property int fontSizeLarge: 16
    readonly property int fontSizeTitle: 20
}
