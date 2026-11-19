import QtQuick
import "../themes"

Item {
    id: root

    property string name: ""
    property int size: 18
    property color color: Theme.textPrimary

    implicitWidth: size
    implicitHeight: size

    // Format color to 6-digit hex without '#' for the provider URL
    readonly property string colorHex: {
        var c = root.color.toString()
        if (c.startsWith("#")) {
            // Remove '#' and if 8-char RGBA, convert to RRGGBB
            return c.length === 9 ? c.substring(3) : c.substring(1)
        }
        return "1E293B"
    }

    Image {
        id: iconImg
        anchors.centerIn: parent
        width: root.size
        height: root.size
        source: root.name ? ("image://icon/" + root.name + "/" + root.colorHex + "/" + (root.size * 2)) : ""
        sourceSize.width: root.size * 2
        sourceSize.height: root.size * 2
        fillMode: Image.PreserveAspectFit
        mipmap: true
        smooth: true
        opacity: root.enabled ? 1.0 : 0.35

        // Fallback to direct SVG file if ImageProvider is not registered
        onStatusChanged: {
            if (status === Image.Error && root.name && !source.toString().startsWith("file:")) {
                source = appController.uiIconsPath + "/" + root.name + ".svg"
            }
        }
    }
}
