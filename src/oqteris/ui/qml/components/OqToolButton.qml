import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Item {
    id: root

    property string iconSymbol: ""
    property bool enabled: true
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

        Text {
            anchors.centerIn: parent
            text: root.iconSymbol
            font.pixelSize: 13
            font.family: "Segoe UI Symbol, sans-serif"
            color: root.enabled ? Theme.textPrimary : Theme.textDisabled
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
