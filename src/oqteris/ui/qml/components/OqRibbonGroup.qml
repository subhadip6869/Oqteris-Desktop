import QtQuick
import "../themes"

Item {
    id: root

    property string title: ""
    default property alias content: contentRow.data

    implicitWidth: Math.max(groupLabel.implicitWidth + 16, contentRow.implicitWidth + 16)
    implicitHeight: 88

    Item {
        anchors.fill: parent

        // Main controls row
        Row {
            id: contentRow
            anchors.top: parent.top
            anchors.topMargin: 2
            anchors.bottom: groupLabel.top
            anchors.bottomMargin: 2
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 3
        }

        // Group title caption beneath buttons
        Text {
            id: groupLabel
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 3
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.title
            font.pixelSize: 10
            font.family: Theme.fontFamily
            color: Theme.textSecondary
        }

        // Vertical divider separating ribbon groups
        Rectangle {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 8
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            width: 1
            color: Theme.divider
        }
    }
}
