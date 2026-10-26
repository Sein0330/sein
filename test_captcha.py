import cv2
import pytesseract
import numpy as np

# Simpen gambar captcha lu sebagai 'captcha_test.png' dulu
img_path = "captcha_test.png" 

def solve_captcha(img_path):
    # 1. Baca grayscale
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return "Error: Gambar gak ketemu"

    # 2. Binarization (Ubah background jadi hitam, teks jadi putih)
    _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)
    
    # 3. Dilasi (Tebelin huruf biar Tesseract gampang baca)
    kernel = np.ones((2,2), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    # 4. Baca pake Tesseract (Mode PSM 8 = treat as single word)
    custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    text = pytesseract.image_to_string(dilated, config=custom_config).strip()
    
    return text

print("Hasil baca CAPTCHA:", solve_captcha(img_path))
