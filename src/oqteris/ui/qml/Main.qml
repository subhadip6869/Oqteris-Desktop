import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import "components"
import "dialogs"
import "panels"
import "pages"
import "ribbon"
import "themes"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1280
    height: 720
    minimumWidth: 980
    minimumHeight: 600
    color: Theme.windowBackground

    title: pdfController.hasDocument ?
        (pdfController.fileName + (pdfController.isModified ? " * - " : " - ") + appController.appDisplayName) :
        appController.appDisplayName

    // Global Panel State
    QtObject {
        id: mainPanelState
        property bool showLeftPanel: false
        property string currentPanelTab: "thumbnails"
        property bool showRightPanel: false

        function togglePanel(tabId) {
            if (showLeftPanel && currentPanelTab === tabId) {
                showLeftPanel = false
            } else {
                currentPanelTab = tabId
                showLeftPanel = true
            }
        }
    }

    Column {
        anchors.fill: parent

        // 1. Quick-Access Toolbar & Window Header (Shown when document is open)
        Rectangle {
            id: quickAccessBar
            width: parent.width
            height: pdfController.hasDocument ? 34 : 0
            visible: pdfController.hasDocument
            clip: true
            color: Theme.titleBarBackground
            border.color: Theme.borderSubtle
            border.width: 1

            Row {
                anchors.left: parent.left
                anchors.leftMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                spacing: 4

                // App Brand Name & Icon
                Row {
                    spacing: 6
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: "🔷"
                        font.pixelSize: 15
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        text: appController.appName
                        font.bold: true
                        font.pixelSize: 13
                        font.family: Theme.fontFamily
                        color: Theme.brandPrimary
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                Rectangle { width: 1; height: 18; color: Theme.divider; anchors.verticalCenter: parent.verticalCenter }

                // Quick Action Buttons
                OqToolButton {
                    iconSymbol: "📂"
                    tooltipText: "Open Document"
                    shortcutText: "Ctrl+O"
                    onClicked: fileDialogLoader.openFile()
                }

                OqToolButton {
                    iconSymbol: "💾"
                    tooltipText: "Save Document"
                    shortcutText: "Ctrl+S"
                    enabled: pdfController.hasDocument && pdfController.isModified
                    onClicked: pdfController.saveDocument()
                }

                OqToolButton {
                    iconSymbol: "↩"
                    tooltipText: "Undo"
                    shortcutText: "Ctrl+Z"
                    enabled: ribbonController.canUndo
                    onClicked: ribbonController.undo()
                }

                OqToolButton {
                    iconSymbol: "↪"
                    tooltipText: "Redo"
                    shortcutText: "Ctrl+Y"
                    enabled: ribbonController.canRedo
                    onClicked: ribbonController.redo()
                }
            }

            // Right header shortcuts (Theme, Settings, About)
            Row {
                anchors.right: parent.right
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6

                // Default Viewer Pill
                Rectangle {
                    width: defaultPillText.implicitWidth + 14
                    height: 22
                    radius: 11
                    color: appController.isDefaultViewer ? Theme.statusSuccess : Theme.selectedBackground
                    visible: !appController.isDefaultViewer
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        id: defaultPillText
                        anchors.centerIn: parent
                        text: "Set as Default PDF Viewer"
                        font.pixelSize: 10
                        color: Theme.brandPrimary
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: appController.requestMakeDefaultViewer()
                    }
                }

                OqToolButton {
                    iconSymbol: appController.isDarkMode ? "☀" : "🌙"
                    tooltipText: "Toggle Theme"
                    onClicked: appController.toggleTheme()
                }

                OqToolButton {
                    iconSymbol: "⚙"
                    tooltipText: "Settings"
                    onClicked: settingsDialogLoader.openSettingsDialog()
                }

                OqToolButton {
                    iconSymbol: "ℹ"
                    tooltipText: "About Oqteris"
                    onClicked: aboutDialogLoader.openAboutDialog()
                }
            }
        }

        // 2. Main Ribbon Bar (Shown when document is open)
        RibbonBar {
            id: mainRibbon
            width: parent.width
            height: pdfController.hasDocument ? 124 : 0
            visible: pdfController.hasDocument
            clip: true
        }

        // 3. Central Application Workspace Area
        Row {
            width: parent.width
            height: parent.height - (pdfController.hasDocument ? (quickAccessBar.height + mainRibbon.height) : 0)

            // Left Navigation Drawer
            NavigationPanel {
                id: leftPanel
                height: parent.height
                visible: pdfController.hasDocument && mainPanelState.showLeftPanel
            }

            // Center Document Workspace
            DocumentWorkspace {
                id: documentWorkspace
                width: parent.width - (leftPanel.visible ? leftPanel.width : 0) - (rightPanel.visible ? rightPanel.width : 0)
                height: parent.height
            }

            // Right Properties Panel
            PropertiesPanel {
                id: rightPanel
                height: parent.height
                visible: pdfController.hasDocument && mainPanelState.showRightPanel
            }
        }
    }

    // --- Dialogs ---

    AboutDialog { id: aboutDlg }
    SettingsDialog { id: settingsDlg }
    SignDialog { id: signDlg }
    CertificateDetailsDialog { id: certDetailsDlg }
    TrustStoreDialog { id: trustStoreDlg }
    OcrDialog { id: ocrDlg }
    OptimizeDialog { id: optimizeDlg }
    PasswordDialog { id: passwordDlg }

    QtObject {
        id: trustStoreDialogLoader
        function openTrustStoreDialog() { trustStoreDlg.open() }
    }

    QtObject {
        id: certDetailsDialogLoader
        function openCertificateDialog(sigIndex) { certDetailsDlg.openForSignature(sigIndex) }
    }

    QtObject {
        id: aboutDialogLoader
        function openAboutDialog() { aboutDlg.open() }
    }

    QtObject {
        id: settingsDialogLoader
        function openSettingsDialog() { settingsDlg.open() }
    }

    QtObject {
        id: signDialogLoader
        function openSignDialog() { signDlg.open() }
        function setCertPath(path) { signDlg.setCertPath(path) }
        function setOutPath(path) { signDlg.setOutPath(path) }
    }

    QtObject {
        id: ocrDialogLoader
        function openOcrDialog() { ocrDlg.open() }
        function setOutPath(path) { ocrDlg.setOutPath(path) }
    }

    QtObject {
        id: optimizeDialogLoader
        function openOptimizeDialog() { optimizeDlg.open() }
        function setOutPath(path) { optimizeDlg.setOutPath(path) }
    }

    Connections {
        target: pdfController
        function onPasswordPromptRequested(filePath) {
            passwordDlg.targetFilePath = filePath
            passwordDlg.open()
        }
        function onErrorOccurred(title, message) {
            errorDlg.title = title
            errorText.text = message
            errorDlg.open()
        }
    }

    Connections {
        target: signatureController
        function onStatusMessageRequested(title, message) {
            infoDlg.title = title
            infoText.text = message
            infoDlg.open()
        }
    }

    Dialog {
        id: infoDlg
        title: "Information"
        modal: true
        anchors.centerIn: parent
        width: 380
        height: 180

        background: Rectangle {
            color: Theme.cardBackground
            border.color: Theme.brandPrimary
            border.width: 1
            radius: 6
        }

        Column {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Text {
                id: infoText
                text: ""
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textPrimary
                wrapMode: Text.WordWrap
                width: parent.width
            }

            Button {
                text: "OK"
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: infoDlg.close()
            }
        }
    }

    Dialog {
        id: errorDlg
        title: "Error"
        modal: true
        anchors.centerIn: parent
        width: 380
        height: 180

        background: Rectangle {
            color: Theme.cardBackground
            border.color: Theme.statusError
            border.width: 1
            radius: 6
        }

        Column {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Text {
                id: errorText
                text: ""
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textPrimary
                wrapMode: Text.WordWrap
                width: parent.width
            }

            Button {
                text: "OK"
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: errorDlg.close()
            }
        }
    }

    // --- Native File Dialogs ---

    FileDialog {
        id: openPdfDialog
        title: "Open PDF Document"
        nameFilters: ["PDF Files (*.pdf)", "All Files (*.*)"]
        onAccepted: pdfController.openDocument(selectedFile.toString())
    }

    FileDialog {
        id: savePdfDialog
        title: "Save PDF Document As"
        fileMode: FileDialog.SaveFile
        nameFilters: ["PDF Files (*.pdf)"]
        defaultSuffix: "pdf"
        onAccepted: pdfController.saveDocumentAs(selectedFile.toString())
    }

    FileDialog {
        id: openCertDialog
        title: "Select PKCS#12 Certificate"
        nameFilters: ["PKCS#12 Certificates (*.p12 *.pfx)", "All Files (*.*)"]
        onAccepted: signDialogLoader.setCertPath(selectedFile.toString())
    }

    FileDialog {
        id: exportCertDialog
        title: "Export Signer Certificate"
        fileMode: FileDialog.SaveFile
        nameFilters: ["Certificate (*.cer *.crt *.pem)", "All Files (*.*)"]
        defaultSuffix: "cer"
        property int targetSigIndex: 0
        onAccepted: signatureController.exportCertificate(targetSigIndex, selectedFile.toString())
    }

    FileDialog {
        id: importCertDialog
        title: "Import Trusted Certificate"
        nameFilters: ["Certificate Files (*.cer *.crt *.pem)", "All Files (*.*)"]
        onAccepted: signatureController.importCertificateFile(selectedFile.toString())
    }

    FileDialog {
        id: saveSignedDialog
        title: "Save Signed PDF As"
        fileMode: FileDialog.SaveFile
        nameFilters: ["PDF Files (*.pdf)"]
        defaultSuffix: "pdf"
        onAccepted: signDialogLoader.setOutPath(selectedFile.toString())
    }

    FileDialog {
        id: saveOcrDialog
        title: "Save Searchable PDF As"
        fileMode: FileDialog.SaveFile
        nameFilters: ["PDF Files (*.pdf)"]
        defaultSuffix: "pdf"
        onAccepted: ocrDialogLoader.setOutPath(selectedFile.toString())
    }

    FileDialog {
        id: saveOptDialog
        title: "Save Compressed PDF As"
        fileMode: FileDialog.SaveFile
        nameFilters: ["PDF Files (*.pdf)"]
        defaultSuffix: "pdf"
        onAccepted: optimizeDialogLoader.setOutPath(selectedFile.toString())
    }

    FileDialog {
        id: saveExtractDialog
        title: "Save Extracted Page As"
        fileMode: FileDialog.SaveFile
        nameFilters: ["PDF Files (*.pdf)"]
        defaultSuffix: "pdf"
        onAccepted: organizeController.extractPages([pdfController.currentPage], selectedFile.toString())
    }

    FolderDialog {
        id: splitFolderDialog
        title: "Select Output Folder for Split PDFs"
        onAccepted: organizeController.splitPdf(selectedFolder.toString(), 1)
    }

    FolderDialog {
        id: exportImagesFolderDialog
        title: "Select Output Folder for Page Images"
        onAccepted: {
            var doc = pdfController.filePath
            if (doc) {
                // Export pages as images
            }
        }
    }

    QtObject {
        id: fileDialogLoader
        function openFile() { openPdfDialog.open() }
        function saveFileAs() { savePdfDialog.open() }
        function openCertificate() { openCertDialog.open() }
        function saveSignedFileAs() { saveSignedDialog.open() }
        function saveOcrFileAs() { saveOcrDialog.open() }
        function saveOptimizedFileAs() { saveOptDialog.open() }
        function saveExtractedPage() { saveExtractDialog.open() }
        function selectSplitOutputDir() { splitFolderDialog.open() }
        function selectExportImagesDir() { exportImagesFolderDialog.open() }
        function openPdfsToMerge() { openPdfDialog.open() }
        function openImagesToConvert() { openPdfDialog.open() }
        function openImageToInsert() { openPdfDialog.open() }
    }

    // --- Global Keyboard Shortcuts ---

    Shortcut {
        sequences: [ StandardKey.Open ]
        onActivated: fileDialogLoader.openFile()
    }

    Shortcut {
        sequences: [ StandardKey.Save ]
        onActivated: {
            if (pdfController.hasDocument) pdfController.saveDocument()
        }
    }

    Shortcut {
        sequences: [ StandardKey.SaveAs ]
        onActivated: {
            if (pdfController.hasDocument) fileDialogLoader.saveFileAs()
        }
    }

    Shortcut {
        sequences: [ StandardKey.Close ]
        onActivated: {
            if (pdfController.hasDocument) pdfController.closeDocument()
        }
    }

    Shortcut {
        sequences: [ StandardKey.Find ]
        onActivated: {
            mainPanelState.showLeftPanel = true
            mainPanelState.currentPanelTab = "search"
        }
    }

    Shortcut {
        sequences: [ StandardKey.Undo ]
        onActivated: ribbonController.undo()
    }

    Shortcut {
        sequences: [ StandardKey.Redo ]
        onActivated: ribbonController.redo()
    }

    Shortcut {
        sequences: [ StandardKey.ZoomIn ]
        onActivated: pdfController.zoomIn()
    }

    Shortcut {
        sequences: [ StandardKey.ZoomOut ]
        onActivated: pdfController.zoomOut()
    }

    Shortcut {
        sequences: [ "Ctrl+0" ]
        onActivated: pdfController.fitPage(documentWorkspace.viewportWidth, documentWorkspace.viewportHeight)
    }

    Shortcut {
        sequences: [ "Ctrl+1" ]
        onActivated: pdfController.actualSize()
    }

    Shortcut {
        sequences: [ "Ctrl+2" ]
        onActivated: pdfController.fitWidth(documentWorkspace.viewportWidth)
    }

    Shortcut {
        sequences: [ "Ctrl+R" ]
        onActivated: pdfController.rotatePage(90)
    }

    Shortcut {
        sequences: [ StandardKey.FullScreen ]
        onActivated: {
            if (mainWindow.visibility === Window.FullScreen) {
                mainWindow.showNormal()
            } else {
                mainWindow.showFullScreen()
            }
        }
    }
}
