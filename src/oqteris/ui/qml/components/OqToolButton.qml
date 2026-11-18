import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Item {
    id: root

    property string iconName: ""
    property string iconSymbol: ""
    property int iconSize: 14
    property bool isChecked: false
    property color iconColor: root.enabled
        ? (root.isChecked ? Theme.brandPrimary : Theme.textPrimary)
        : Theme.textDisabled
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
            if (root.isChecked) return Theme.selectedBackground
            if (mouseArea.containsMouse) return Theme.buttonHover
            return "transparent"
        }
        border.color: root.isChecked ? Theme.borderFocused : "transparent"
        border.width: root.isChecked ? 1 : 0

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
