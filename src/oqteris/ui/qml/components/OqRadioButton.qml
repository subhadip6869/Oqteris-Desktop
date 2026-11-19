import QtQuick
import "../themes"

Item {
    id: root

    property string text: ""
    property bool checked: false
    property bool enabled: true

    signal clicked()

    implicitWidth: radioRow.implicitWidth
    implicitHeight: 22

    Row {
        id: radioRow
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8

        // Native-styled compact radio button indicator (15x15)
        Rectangle {
            id: indicator
            width: 15
            height: 15
            radius: 7.5
            anchors.verticalCenter: parent.verticalCenter

            color: {
                if (!root.enabled) return Theme.isDark ? "#2A2A2A" : "#F0F0F0"
                if (mouseArea.containsMouse) return Theme.buttonHover
                return Theme.isDark ? "#252525" : "#FFFFFF"
            }

            border.color: {
                if (!root.enabled) return Theme.borderSubtle
                if (root.checked) return Theme.brandPrimary
                if (mouseArea.containsMouse) return Theme.brandHover
                return Theme.isDark ? "#555555" : "#ABABAB"
            }
            border.width: root.checked ? 1.5 : 1

            // Center filled circle when checked
            Rectangle {
                anchors.centerIn: parent
                width: 7
                height: 7
                radius: 3.5
                color: root.enabled ? Theme.brandPrimary : Theme.textDisabled
                visible: root.checked
            }
        }

        Text {
            id: label
            anchors.verticalCenter: parent.verticalCenter
            text: root.text
            font.pixelSize: Theme.fontSizeSmall
            font.family: Theme.fontFamily
            color: root.enabled ? Theme.textPrimary : Theme.textDisabled
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        enabled: root.enabled

        onClicked: {
            if (!root.checked) {
                root.checked = true
            }
            root.clicked()
        }
    }
}
