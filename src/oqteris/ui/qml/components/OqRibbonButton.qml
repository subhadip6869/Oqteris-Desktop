import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Item {
    id: root

    property string text: ""
    property string iconSymbol: ""  // Unicode icon character or symbol
    property string iconSource: ""
    property bool isLarge: true
    property bool isChecked: false
    property string tooltipText: ""
    property string shortcutText: ""

    signal clicked()

    implicitWidth: isLarge ? Math.max(54, btnText.implicitWidth + 12) : Math.max(48, rowContent.implicitWidth + 12)
    implicitHeight: isLarge ? 68 : 30

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: 3
        color: {
            if (!root.enabled) return "transparent"
            if (mouseArea.pressed) return Theme.buttonPressed
            if (root.isChecked) return Theme.selectedBackground
            if (mouseArea.containsMouse) return Theme.buttonHover
            return "transparent"
        }
        border.color: root.isChecked ? Theme.brandPrimary : "transparent"
        border.width: 1

        Behavior on color { ColorAnimation { duration: 100 } }

        // Large button layout: Vertical (Icon top, Label bottom)
        Column {
            anchors.centerIn: parent
            spacing: 2
            visible: root.isLarge

            Text {
                id: iconTextLarge
                text: root.iconSymbol
                font.pixelSize: 22
                font.family: "Segoe UI Symbol, sans-serif"
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                color: root.enabled ? (root.isChecked ? Theme.brandPrimary : Theme.textPrimary) : Theme.textDisabled
            }

            Text {
                id: btnText
                text: root.text
                font.pixelSize: Theme.fontSizeSmall
                font.family: Theme.fontFamily
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                color: root.enabled ? Theme.textPrimary : Theme.textDisabled
                elide: Text.ElideRight
                maximumLineCount: 2
                wrapMode: Text.WordWrap
            }
        }

        // Compact button layout: Horizontal (Icon left, Label right)
        Row {
            id: rowContent
            anchors.centerIn: parent
            spacing: 6
            visible: !root.isLarge

            Text {
                text: root.iconSymbol
                font.pixelSize: 14
                font.family: "Segoe UI Symbol, sans-serif"
                anchors.verticalCenter: parent.verticalCenter
                color: root.enabled ? (root.isChecked ? Theme.brandPrimary : Theme.textPrimary) : Theme.textDisabled
            }

            Text {
                text: root.text
                font.pixelSize: Theme.fontSizeSmall
                font.family: Theme.fontFamily
                anchors.verticalCenter: parent.verticalCenter
                color: root.enabled ? Theme.textPrimary : Theme.textDisabled
                visible: root.text.length > 0
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
        ToolTip.delay: 400
        ToolTip.text: root.shortcutText ? (root.tooltipText + " (" + root.shortcutText + ")") : root.tooltipText
    }
}
