import qrcode
import cv2
import numpy as np
import sys
import math
from pyzbar.pyzbar import decode

PATTERN_POSITION_TABLE = [
    [],
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
    [6, 24, 42],
    [6, 26, 46],
    [6, 28, 50],
    [6, 30, 54],
    [6, 32, 58],
    [6, 34, 62],
    [6, 26, 46, 66],
    [6, 26, 48, 70],
    [6, 26, 50, 74],
    [6, 30, 54, 78],
    [6, 30, 56, 82],
    [6, 30, 58, 86],
    [6, 34, 62, 90],
    [6, 28, 50, 72, 94],
    [6, 26, 50, 74, 98],
    [6, 30, 54, 78, 102],
    [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110],
    [6, 30, 58, 86, 114],
    [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122],
    [6, 30, 54, 78, 102, 126],
    [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134],
    [6, 34, 60, 86, 112, 138],
    [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146],
    [6, 30, 54, 78, 102, 126, 150],
    [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158],
    [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166],
    [6, 30, 58, 86, 114, 142, 170],
]

def _text_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def _xor(a, b):
    if a == b:
        return 0
    return 255

def is_inside_corner(row, col, height, width, corner_size):
    return (row < corner_size and col < corner_size) or \
                        (row < corner_size and col >= width - corner_size) or \
                        (row >= height - corner_size and col < corner_size) or \
                        (row == 7) or (col == 7) or \
                        (row >= height - (corner_size + 2) and col < 7) or \
                        (col >= height - (corner_size + 2) and row < 7)

def is_inside_pattern(version, row, col):
    for pos1 in PATTERN_POSITION_TABLE[version -1]:
        for pos2 in PATTERN_POSITION_TABLE[version -1]:
            distance = math.sqrt((row - pos1)**2 + (col - pos2)**2)
            if distance < 3:
                    return True
    return False

def is_on_border(row, col, height, width):
    return not(0 < row < height - 1 and 0 < col < width - 1)

def encrypt(cover_message, payload, version=1):
    qr = qrcode.QRCode(
        version = version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=1
    )
    qr.add_data(cover_message)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("original_qr_code.png")

    total_codewords = (4*qr.version+17)**2
    total_changeable_bits = total_codewords * 0.30

    payload = _text_to_binary(payload) + '11111111'
    num_changed_bits = len(payload)
    if num_changed_bits < total_changeable_bits:
        print("The payload can be embedded")
    else:
        print("Choose a shorter payload or a longer message")
        sys.exit()
    
    og_qr_code = cv2.imread("original_qr_code.png")
    og_qr_code = cv2.cvtColor(og_qr_code, cv2.COLOR_BGR2GRAY)
    height, width = og_qr_code.shape
    blank_image = np.zeros((height, width))

    corner_size=9 #Set to nine to avoid version pattern, format information and quiet zones
    n = 0
    while len(payload) > 0 or n < height*width:
        row = n // width
        col = n % width
        in_corner = is_inside_corner (row, col,height, width, corner_size)
        in_pattern = is_inside_pattern(qr.version, row, col)
        in_border = is_on_border(row, col, height, width)
        if not in_corner and not in_pattern and not in_border:
            if payload != "":
                if payload[0] == "1":
                    blank_image[row, col] = 255
                else:
                    blank_image[row, col] = 0
                payload = payload[1:]
        n += 1
    
    cv2.imwrite("flipped_pixels.png", blank_image)
    resulting_qr_code = cv2.imread("original_qr_code.png")

    for row in range(height):
        for col in range(width):
                    resulting_qr_code[row, col] = _xor(og_qr_code[row,col], blank_image[row,col])
                    in_corner = is_inside_corner (row, col,height, width, corner_size)
                    in_pattern = is_inside_pattern(qr.version, row, col)
                    in_border = is_on_border(row, col, height, width)

    if decode(resulting_qr_code) == []:
        print("Error in embedding, use a higher version, a longer cover or a shorter payload")
    # cv2.imwrite("resulting_qr_code.png", resulting_qr_code)
    return resulting_qr_code

def decrypt(qr_code_path):
    steg_qr = cv2.imread(qr_code_path)

    gray = cv2.cvtColor(steg_qr, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    corner_size=9
    version = (height-18)//4

    qr_codes = decode(gray)
    if qr_codes == []:
        sys.exit()
    for qr_code in qr_codes:
        qr_data = qr_code.data.decode('utf-8')
        qr_version = version
        print(f"Original QR code data: {qr_data}")

    qr = qrcode.QRCode(
        version = qr_version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=1
    )

    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("correct_qr.png")
    correct_qr = cv2.imread("correct_qr.png")
    correct_qr = cv2.cvtColor(correct_qr, cv2.COLOR_BGR2GRAY)

    n = 0
    message = ""
    bits = ""
    finished = False
    while not finished :
        row = n // width
        col = n % width
        in_corner = is_inside_corner (row, col,height, width, corner_size)
        in_pattern = is_inside_pattern(qr_version, row, col)
        in_border = is_on_border(row, col, height, width)
        if not in_corner and not in_pattern and not in_border:
            if _xor(correct_qr[row, col], gray[row,col]) == 0:
                bits += '0'
            else:
                bits += '1'
            if len(bits) % 8 == 0:
                if bits == '11111111':
                    finished = True
                    break
                message += chr(int(bits[:8], 2))
                bits = bits[8:]
        n += 1
    return message
