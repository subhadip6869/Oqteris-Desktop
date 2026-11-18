import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Item {
    id: root

    property string iconName: ""
    property string iconSymbol: ""
    property int iconSize: 14
    property color iconColor: root.enabled ? (appController.isDarkMode ? "#60A5FA" : "#2563EB") : Theme.textDisabled
    property string tooltipText: ""
    property string shortcutText: ""

    signal clicked()

    implicitWidth: 26
    implicitHeight: 24

    Rectangle {
        anchors.fill: parent
        radius: 3
        color: {
            if (!root.enabled) return "transparent"
            if (mouseArea.pressed) return Theme.buttonPressed
            if (mouseArea.containsMouse) return Theme.buttonHover
            return "transparent"
        }

        OqIcon {
            anchors.centerIn: parent
            size: root.iconSize
            name: root.iconName
            color: root.iconColor
            visible: root.iconName.length > 0
        }

        Text {
            anchors.centerIn: parent
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            text: root.iconSymbol
            font.pixelSize: 12
            font.family: "Segoe UI Symbol, Segoe UI, sans-serif"
            color: root.iconColor
            visible: root.iconName.length === 0 && root.iconSymbol.length > 0
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
