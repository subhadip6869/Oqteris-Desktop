import QtQuick
import "../themes"

Item {
    id: root

    property real from: 0.0
    property real to: 100.0
    property real value: 50.0
    property real stepSize: 1.0
    property bool enabled: true

    signal moved()
    signal valueChangedByUser(real val)

    implicitWidth: 140
    implicitHeight: 22

    // Internal normalized position [0, 1]
    readonly property real position: (to > from) ? Math.max(0, Math.min(1, (value - from) / (to - from))) : 0.0

    function setValueFromX(mouseX) {
        var trackStart = 6
        var trackEnd = width - 6
        var availableW = trackEnd - trackStart
        if (availableW <= 0) return
        var pos = Math.max(0, Math.min(1, (mouseX - trackStart) / availableW))
        var rawVal = from + pos * (to - from)
        if (stepSize > 0) {
            rawVal = Math.round((rawVal - from) / stepSize) * stepSize + from
        }
        rawVal = Math.max(from, Math.min(to, rawVal))
        root.value = rawVal
        root.moved()
        root.valueChangedByUser(rawVal)
    }

    // Groove background track
    Rectangle {
        id: trackBg
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 6
        anchors.rightMargin: 6
        anchors.verticalCenter: parent.verticalCenter
        height: 4
        radius: 2
        color: Theme.isDark ? "#383838" : "#D0D0D0"

        // Active highlighted groove portion
        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: root.position * parent.width
            radius: 2
            color: root.enabled ? Theme.brandPrimary : Theme.textDisabled
        }
    }

    // Native-styled compact slider thumb / handle
    Rectangle {
        id: handle
        width: 13
        height: 13
        radius: 6.5
        anchors.verticalCenter: parent.verticalCenter
        x: 6 + root.position * (root.width - 12 - 13)

        color: {
            if (!root.enabled) return Theme.isDark ? "#404040" : "#E0E0E0"
            if (sliderMouse.pressed) return Theme.brandHover
            if (sliderMouse.containsMouse) return Theme.isDark ? "#FFFFFF" : "#FFFFFF"
            return Theme.isDark ? "#CCCCCC" : "#FFFFFF"
        }

        border.color: {
            if (!root.enabled) return Theme.borderSubtle
            if (sliderMouse.pressed || sliderMouse.containsMouse) return Theme.brandPrimary
            return Theme.isDark ? "#666666" : "#A0A0A0"
        }
        border.width: 1.5

        // Subtle drop shadow for native desktop feel
        Rectangle {
            anchors.centerIn: parent
            width: parent.width + 2
            height: parent.height + 2
            radius: parent.radius + 1
            z: -1
            color: "#1A000000"
            visible: !Theme.isDark
        }
    }

    MouseArea {
        id: sliderMouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        enabled: root.enabled

        onPressed: (mouse) => root.setValueFromX(mouse.x)
        onPositionChanged: (mouse) => {
            if (pressed) {
                root.setValueFromX(mouse.x)
            }
        }
    }
}
