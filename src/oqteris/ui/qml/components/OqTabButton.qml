import QtQuick
import "../themes"

Item {
    id: root

    property string text: ""
    property bool isSelected: false
    property string badgeText: ""

    signal clicked()

    implicitWidth: label.implicitWidth + 24
    implicitHeight: 30

    Rectangle {
        id: bg
        anchors.fill: parent
        color: {
            if (root.isSelected) return Theme.ribbonBackground
            if (mouseArea.containsMouse) return Theme.buttonHover
            return "transparent"
        }

        // Active indicator line at bottom
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 2.5
            color: Theme.brandPrimary
            visible: root.isSelected
        }

        Text {
            id: label
            anchors.centerIn: parent
            text: root.text
            font.pixelSize: Theme.fontSizeSmall
            font.family: Theme.fontFamily
            font.weight: root.isSelected ? Font.DemiBold : Font.Normal
            color: root.isSelected ? Theme.brandPrimary : Theme.textPrimary
        }

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.clicked()
        }
    }
}
