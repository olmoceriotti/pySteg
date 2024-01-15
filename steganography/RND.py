import cv2
import random

def _text_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def _xor(a, b):
    if a == b:
        return '0'
    return '1'

class NoSeedException(Exception):
    def __init__(self, message="No valid seed provided!"):
        self.message = message
        super().__init__(self.message)


def encrypt(message, image_path, seed):
    if seed is None:
        raise NoSeedException()
    random.seed(seed)
    print(f"The seed is {seed}")

    occupied_pixels = []
    image = cv2.imread(image_path)
    height, width, channels = image.shape
    upper_bound = height * width -1

    str_message = message
    message = _text_to_binary(message)

    for i in range(0, len(str_message) + 1):
        n = random.randint(0, upper_bound)
        while(n in occupied_pixels):
            n = random.randint(0, upper_bound)
        occupied_pixels.append(n)
        bits = message[:8]
        message = message[8:]
        row = int(n / width)
        col = int(n % width)

        for channel in range(0, channels):
            offset = 0
            
            pixel = bin(image[row, col][channel])[2:].zfill(8)

            if len(bits) > 3:
                bit = bits[:3]
                bits = bits[3:]
            else:
                bit = bits
                offset = 1

            for j in range(0, len(bit)):
                n2 = random.randint(0, 4)
                msb = pixel[n2] # OK
                pixel = pixel[:(5 + offset + j)] + _xor(msb, bit[j]) + pixel[(5 + offset + j + 1):]
            image[row, col][channel] = int(pixel, 2)

    return image

def decrypt(image_path, seed):
    if seed is None:
        raise NoSeedException()
    random.seed(seed)
    occupied_pixels = []
    image = cv2.imread(image_path)
    height, width, channels = image.shape
    upper_bound = height * width -1
    message = ""
    while '\0' not in message:
        n = random.randint(0, upper_bound)
        while(n in occupied_pixels):
            n = random.randint(0, upper_bound)
        occupied_pixels.append(n)

        row = int(n / width)
        col = int(n % width)

        tot_bits = 8
        
        buffer = ""
        for channel in range(0, channels):
            pixel = image[row, col]
            offset = 0
            pix_bits = bin(pixel[channel])[2:].zfill(8)
            if tot_bits > 3:
                bits = 3
                tot_bits -= 3
            else:
                bits = tot_bits
                offset = 1

            for i in range(0, bits):
                n2 = random.randint(0, 4)
                msb = pix_bits[n2]
                buffer += _xor(pix_bits[5 + i + offset], msb)

        message += chr(int(buffer, 2))

    return message
    