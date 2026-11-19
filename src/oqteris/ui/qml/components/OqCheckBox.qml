import QtQuick
import "../themes"

Item {
    id: root

    property string text: ""
    property bool checked: false
    property bool enabled: true

    signal toggled(bool checked)

    implicitWidth: checkRow.implicitWidth
    implicitHeight: 22

    Row {
        id: checkRow
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8

        // Native-styled compact checkbox indicator (15x15)
        Rectangle {
            id: indicator
            width: 15
            height: 15
            radius: 3
            anchors.verticalCenter: parent.verticalCenter

            color: {
                if (!root.enabled) return Theme.isDark ? "#2A2A2A" : "#F0F0F0"
                if (root.checked) return Theme.brandPrimary
                if (mouseArea.containsMouse) return Theme.buttonHover
                return Theme.isDark ? "#252525" : "#FFFFFF"
            }

            border.color: {
                if (!root.enabled) return Theme.borderSubtle
                if (root.checked) return Theme.brandPrimary
                if (mouseArea.containsMouse) return Theme.brandHover
                return Theme.isDark ? "#555555" : "#ABABAB"
            }
            border.width: 1

            // Crisp checkmark icon
            Canvas {
                id: checkCanvas
                anchors.centerIn: parent
                width: 11
                height: 9
                visible: root.checked

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.reset();
                    ctx.strokeStyle = "#FFFFFF";
                    ctx.lineWidth = 1.8;
                    ctx.lineCap = "round";
                    ctx.lineJoin = "round";

                    ctx.beginPath();
                    ctx.moveTo(1.5, 4.5);
                    ctx.lineTo(4.2, 7.5);
                    ctx.lineTo(9.5, 1.5);
                    ctx.stroke();
                }

                Connections {
                    target: root
                    function onCheckedChanged() { checkCanvas.requestPaint() }
                }
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
            root.checked = !root.checked
            root.toggled(root.checked)
        }
    }
}
