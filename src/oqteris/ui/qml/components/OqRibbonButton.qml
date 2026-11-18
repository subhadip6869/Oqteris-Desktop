import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Item {
    id: root

    property string text: ""
    property string iconName: ""
    property string iconSymbol: ""
    property bool isLarge: true
    property bool isChecked: false
    property bool hasDropdown: false
    property string tooltipText: ""
    property string shortcutText: ""

    signal clicked()

    implicitWidth: isLarge
        ? Math.max(46, Math.max(btnText.implicitWidth + 10, (hasDropdown ? dropdownRow.implicitWidth + 6 : 38)))
        : Math.max(42, rowContent.implicitWidth + 8)
    implicitHeight: isLarge ? 64 : 26

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: root.isChecked ? 5 : 4
        color: {
            if (!root.enabled) return "transparent"
            if (mouseArea.pressed) return appController.isDarkMode ? "#333842" : "#E2E8F0"
            if (root.isChecked) return appController.isDarkMode ? "#1E293B" : "#EFF6FF"
            if (mouseArea.containsMouse) return appController.isDarkMode ? "#272A30" : "#F1F5F9"
            return "transparent"
        }
        border.color: {
            if (root.isChecked) return "#2563EB"
            if (mouseArea.containsMouse) return appController.isDarkMode ? "#3F4450" : "#CBD5E1"
            return "transparent"
        }
        border.width: root.isChecked ? 1.5 : 1

        Behavior on color { ColorAnimation { duration: 80 } }

        // Large button layout: Vertical (Icon top, Label bottom)
        Column {
            anchors.centerIn: parent
            spacing: 3
            visible: root.isLarge

            Item {
                id: iconContainer
                width: 24
                height: 24
                anchors.horizontalCenter: parent.horizontalCenter

                OqIcon {
                    id: oqIconLarge
                    anchors.centerIn: parent
                    size: 22
                    name: root.iconName
                    color: root.enabled
                        ? (root.isChecked ? "#1D4ED8" : (appController.isDarkMode ? "#60A5FA" : "#2563EB"))
                        : Theme.textDisabled
                    visible: root.iconName.length > 0
                }

                Text {
                    id: iconTextLarge
                    anchors.centerIn: parent
                    text: root.iconSymbol
                    font.pixelSize: 18
                    font.family: "Segoe UI Symbol, sans-serif"
                    color: root.enabled
                        ? (root.isChecked ? "#1D4ED8" : (appController.isDarkMode ? "#60A5FA" : "#2563EB"))
                        : Theme.textDisabled
                    visible: root.iconName.length === 0 && root.iconSymbol.length > 0
                }
            }

            Row {
                id: dropdownRow
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 3

                Text {
                    id: btnText
                    text: root.text
                    font.pixelSize: 11
                    font.family: Theme.fontFamily
                    font.weight: root.isChecked ? Font.DemiBold : Font.Normal
                    horizontalAlignment: Text.AlignHCenter
                    anchors.verticalCenter: parent.verticalCenter
                    color: root.enabled
                        ? (root.isChecked ? "#1D4ED8" : (appController.isDarkMode ? "#F1F5F9" : "#1E293B"))
                        : Theme.textDisabled
                    elide: Text.ElideRight
                    maximumLineCount: 2
                    wrapMode: Text.WordWrap
                }

                OqIcon {
                    anchors.verticalCenter: parent.verticalCenter
                    size: 9
                    name: "chevron-down"
                    color: root.enabled ? (appController.isDarkMode ? "#94A3B8" : "#64748B") : Theme.textDisabled
                    visible: root.hasDropdown
                }
            }
        }

        // Compact button layout: Horizontal (Icon left, Label right)
        Row {
            id: rowContent
            anchors.centerIn: parent
            spacing: 6
            visible: !root.isLarge

            OqIcon {
                anchors.verticalCenter: parent.verticalCenter
                size: 15
                name: root.iconName
                color: root.enabled
                    ? (root.isChecked ? "#1D4ED8" : (appController.isDarkMode ? "#60A5FA" : "#2563EB"))
                    : Theme.textDisabled
                visible: root.iconName.length > 0
            }

            Text {
                text: root.iconSymbol
                font.pixelSize: 13
                font.family: "Segoe UI Symbol, sans-serif"
                anchors.verticalCenter: parent.verticalCenter
                color: root.enabled
                    ? (root.isChecked ? "#1D4ED8" : (appController.isDarkMode ? "#60A5FA" : "#2563EB"))
                    : Theme.textDisabled
                visible: root.iconName.length === 0 && root.iconSymbol.length > 0
            }

            Text {
                text: root.text
                font.pixelSize: 11
                font.family: Theme.fontFamily
                font.weight: root.isChecked ? Font.DemiBold : Font.Normal
                anchors.verticalCenter: parent.verticalCenter
                color: root.enabled
                    ? (root.isChecked ? "#1D4ED8" : (appController.isDarkMode ? "#F1F5F9" : "#1E293B"))
                    : Theme.textDisabled
                visible: root.text.length > 0
            }

            OqIcon {
                anchors.verticalCenter: parent.verticalCenter
                size: 8
                name: "chevron-down"
                color: root.enabled ? (appController.isDarkMode ? "#94A3B8" : "#64748B") : Theme.textDisabled
                visible: root.hasDropdown
            }
        }

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            enabled: root.enabled
            cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
            onClicked: root.clicked()
        }

        ToolTip.visible: mouseArea.containsMouse && (root.tooltipText.length > 0 || root.shortcutText.length > 0)
        ToolTip.delay: 350
        ToolTip.text: root.shortcutText ? (root.tooltipText + " (" + root.shortcutText + ")") : root.tooltipText
    }
}
