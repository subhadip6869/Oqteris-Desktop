# OCR Capabilities and Configuration

Oqteris provides optical character recognition (OCR) to convert scanned, image-only documents into fully searchable, selectable PDF documents.

## Technology Stack

- **Tesseract OCR**: Recognition engine producing text and bounding boxes.
- **OCRmyPDF / pytesseract**: Searchable PDF generation with text layers.
- **OpenCV**: Image preprocessing prior to recognition.

## Preprocessing Pipeline

Scanned documents often suffer from rotation skew, low contrast, or noise. Before text recognition, Oqteris runs an OpenCV pipeline:
1. **Deskewing**: Calculates orientation angle via `cv2.minAreaRect` on Otsu threshold contours and corrects affine rotation.
2. **Contrast Enhancement / Binarization**: Applies median blur denoising and adaptive Gaussian thresholding.

## External Tool Detection

Oqteris detects Tesseract automatically across standard system paths:
- Windows: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- Linux: `/usr/bin/tesseract`
- macOS: `/opt/homebrew/bin/tesseract`
- Custom paths configured in application Settings.

If Tesseract is not detected, Oqteris displays a friendly notification with installation guidance and direct links.
