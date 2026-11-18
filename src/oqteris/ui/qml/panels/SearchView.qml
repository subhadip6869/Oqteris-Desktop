import QtQuick
import QtQuick.Controls
import "../components"
import "../themes"

Item {
    id: root

    Column {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 10

        Text {
            text: "Find in Document"
            font.pixelSize: Theme.fontSizeMedium
            font.weight: Font.DemiBold
            color: Theme.textPrimary
        }

        // Search Input
        Rectangle {
            width: parent.width
            height: 32
            radius: 4
            color: Theme.cardBackground
            border.color: searchInput.activeFocus ? Theme.borderFocused : Theme.borderSubtle
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                TextInput {
                    id: searchInput
                    width: parent.width - 60
                    anchors.verticalCenter: parent.verticalCenter
                    font.pixelSize: Theme.fontSizeNormal
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                    selectByMouse: true
                    onAccepted: pdfController.search(text, caseCheck.checked)
                }

                Rectangle {
                    width: 24
                    height: 24
                    radius: 3
                    color: searchBtnMouse.containsMouse ? Theme.buttonHover : "transparent"
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        anchors.centerIn: parent
                        text: "🔍"
                        font.pixelSize: 12
                    }

                    MouseArea {
                        id: searchBtnMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: pdfController.search(searchInput.text, caseCheck.checked)
                    }
                }

                Rectangle {
                    width: 24
                    height: 24
                    radius: 3
                    color: clearBtnMouse.containsMouse ? Theme.buttonHover : "transparent"
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        anchors.centerIn: parent
                        text: "✕"
                        font.pixelSize: 11
                        color: Theme.textSecondary
                    }

                    MouseArea {
                        id: clearBtnMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            searchInput.text = ""
                            pdfController.clearSearch()
                        }
                    }
                }
            }
        }

        Row {
            spacing: 8
            OqCheckBox {
                id: caseCheck
                text: "Match Case"
            }
        }

        Row {
            spacing: 8
            visible: pdfController.searchMatchCount > 0

            Text {
                text: (pdfController.currentSearchResultIndex + 1) + " of " + pdfController.searchMatchCount + " matches"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                anchors.verticalCenter: parent.verticalCenter
            }

            Rectangle {
                width: 28
                height: 24
                radius: 3
                color: prevMatchMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                border.color: Theme.borderSubtle
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "▲"
                    font.pixelSize: 10
                }

                MouseArea {
                    id: prevMatchMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: pdfController.prevSearchResult()
                }
            }

            Rectangle {
                width: 28
                height: 24
                radius: 3
                color: nextMatchMouse.containsMouse ? Theme.buttonHover : Theme.cardBackground
                border.color: Theme.borderSubtle
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "▼"
                    font.pixelSize: 10
                }

                MouseArea {
                    id: nextMatchMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: pdfController.nextSearchResult()
                }
            }
        }

        ListView {
            width: parent.width
            height: parent.height - 130
            clip: true
            spacing: 4
            model: pdfController.searchResults

            delegate: Rectangle {
                width: parent.width
                height: 36
                color: index === pdfController.currentSearchResultIndex ? Theme.selectedBackground : (matchMouse.containsMouse ? Theme.buttonHover : "transparent")
                radius: 3

                Row {
                    anchors.fill: parent
                    anchors.margins: 6
                    spacing: 8

                    Text {
                        text: "Page " + (modelData.pageIndex + 1)
                        font.pixelSize: Theme.fontSizeSmall
                        font.weight: Font.DemiBold
                        color: Theme.brandPrimary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        text: modelData.snippet
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textPrimary
                        elide: Text.ElideRight
                        width: parent.width - 70
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                MouseArea {
                    id: matchMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        pdfController.goToPage(modelData.pageIndex)
                    }
                }
            }
        }
    }
}
