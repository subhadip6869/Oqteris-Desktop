import QtQuick
import "../themes"

Item {
    id: root

    property string text: ""
    property bool isPrimary: false
    property string iconName: ""
    property string iconSymbol: ""
    property bool enabled: true

    signal clicked()

    implicitWidth: Math.max(72, btnRow.implicitWidth + 24)
    implicitHeight: 28

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: 4

        color: {
            if (!root.enabled) {
                return root.isPrimary
                    ? (Theme.isDark ? "#1C4E72" : "#99C2E6")
                    : (Theme.isDark ? "#242424" : "#F3F3F3")
            }
            if (mouseArea.pressed) {
                return root.isPrimary ? Theme.brandPressed : Theme.buttonPressed
            }
            if (mouseArea.containsMouse) {
                return root.isPrimary ? Theme.brandHover : Theme.buttonHover
            }
            return root.isPrimary
                ? Theme.brandPrimary
                : (Theme.isDark ? "#2D2D2D" : "#FFFFFF")
        }

        border.color: {
            if (root.isPrimary) return "transparent"
            if (!root.enabled) return Theme.borderSubtle
            if (mouseArea.containsMouse) return Theme.borderFocused
            return Theme.isDark ? "#484848" : "#CCCCCC"
        }
        border.width: root.isPrimary ? 0 : 1

        Row {
            id: btnRow
            anchors.centerIn: parent
            spacing: 6

            OqIcon {
                anchors.verticalCenter: parent.verticalCenter
                size: 14
                name: root.iconName
                color: root.isPrimary
                    ? "#FFFFFF"
                    : (root.enabled ? Theme.textPrimary : Theme.textDisabled)
                visible: root.iconName.length > 0
            }

            Text {
                id: label
                anchors.verticalCenter: parent.verticalCenter
                text: root.text
                font.pixelSize: Theme.fontSizeSmall
                font.family: Theme.fontFamily
                font.weight: root.isPrimary ? Font.Medium : Font.Normal
                color: {
                    if (!root.enabled) return Theme.textDisabled
                    if (root.isPrimary) return "#FFFFFF"
                    return Theme.textPrimary
                }
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        enabled: root.enabled

        onClicked: root.clicked()
    }
}
