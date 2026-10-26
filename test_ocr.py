import cv2
import pytesseract
import numpy as np

def solve_captcha_hardcore(img_path):
    # 1. Baca gambar
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return "Gambar gak ada"

    # 2. Resize (Zoom 3x biar teks lebih tebal)
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    
    # 3. Adaptive Thresholding (Paksa jadi hitam-putih tegas)
    thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # 4. Morphological Opening (Hilangin titik-titik noise)
    kernel = np.ones((3,3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 5. Morphological Closing (Tebelin huruf)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Simpen hasil editan biar lu bisa liat
    cv2.imwrite("captcha_hardcore.png", closing)
    
    # 6. Tesseract PSM 8 (Treat as single word)
    custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789'
    text = pytesseract.image_to_string(closing, config=custom_config).strip()
    
    # Bersihin karakter aneh
    text = ''.join(e for e in text if e.isalnum())
    return text

print("Hasil baca:", solve_captcha_hardcore("last_captcha.png"))
