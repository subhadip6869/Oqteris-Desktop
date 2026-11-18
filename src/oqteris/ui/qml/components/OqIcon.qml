import QtQuick
import "../themes"

Item {
    id: root

    property string name: ""
    property int size: 18
    property color color: Theme.brandPrimary

    implicitWidth: size
    implicitHeight: size

    Image {
        id: iconImg
        anchors.centerIn: parent
        width: root.size
        height: root.size
        source: root.name ? (appController.ribbonIconsPath + "/" + root.name + ".svg") : ""
        sourceSize.width: root.size * 2
        sourceSize.height: root.size * 2
        fillMode: Image.PreserveAspectFit
        mipmap: true
        smooth: true
        opacity: root.enabled ? 1.0 : 0.35
    }
}
