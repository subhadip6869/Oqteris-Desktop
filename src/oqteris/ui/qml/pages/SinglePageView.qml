import QtQuick
import QtQuick.Controls.Basic
import "../themes"

Flickable {
    id: root
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    contentWidth: Math.max(width, paperSheet.width + 40)
    contentHeight: Math.max(height, paperSheet.height + 40)

    Rectangle {
        id: paperSheet
        x: Math.max(20, (root.contentWidth - width) / 2)
        y: Math.max(20, (root.contentHeight - height) / 2)
        width: pageImage.width
        height: pageImage.height
        color: "#FFFFFF"
        border.color: Theme.borderSubtle
        border.width: 1

        Image {
            id: pageImage
            width: {
                var geoms = pdfController.pageGeometries
                if (geoms && pdfController.currentPage < geoms.length) {
                    return geoms[pdfController.currentPage].width * pdfController.zoomLevel
                }
                return 612 * pdfController.zoomLevel
            }
            height: {
                var geoms = pdfController.pageGeometries
                if (geoms && pdfController.currentPage < geoms.length) {
                    return geoms[pdfController.currentPage].height * pdfController.zoomLevel
                }
                return 792 * pdfController.zoomLevel
            }
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            cache: false
            smooth: true
            mipmap: true
            source: pdfController.hasDocument ?
                ("image://pdf/" + pdfController.activeDocId + "/" + pdfController.currentPage +
                 "?zoom=" + pdfController.zoomLevel +
                 "&rot=" + pdfController.rotation +
                 "&v=" + pdfController.renderNonce) : ""
        }
    }
}
