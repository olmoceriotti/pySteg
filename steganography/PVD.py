import cv2
import math

def _text_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def _embed_info_gen(n):
    squares = (0, 2, 4, 6, 8, 16, 32, 64, 128, 192, 256)
    l , r = 0, len(squares) - 1
    while r - l > 1:
        mid = (l + r) // 2
        if squares[mid] >= n:
            r = mid
        else:
            l = mid
    return int(math.log2(squares[r] - squares[l])), squares[l], squares[r]

def _change_difference(a, b, dif, newdif):
    swap = False
    if a > b:
        a, b = b, a
        swap = True
    
    upper_add = abs(newdif - dif) // 2 + abs(newdif - dif) % 2
    lower_add = abs(newdif - dif) // 2

    if newdif > dif:
        if a - upper_add < 0:
            shift = upper_add - a
            upper_add -= shift
            lower_add += shift

        if b + lower_add > 255:
            shift = b + lower_add - 255
            lower_add -= shift
            upper_add += shift

        a -= upper_add
        b += lower_add
    else:
        a += upper_add
        b -= lower_add

    if swap:
        a, b = b, a
    return a, b

def encrypt(message, image_path, seed):
    image = cv2.imread(image_path)
    height, width, channels = image.shape
    width -= width % 2

    str_message = message
    message = _text_to_binary(str_message)

    row = 0
    flag = True
    while row < height and flag:
        for col in range(0, width, 2):
            for channel in range(channels):
                pix_1 = int(image[row, col][channel])
                pix_2 = int(image[row, col + 1][channel])

                difference = abs(pix_1-pix_2)

                embed_info = _embed_info_gen(difference)
                if message == '':
                    flag = True
                    break
                bits = int(''.join(message[:embed_info[0]]), base=2)

                difference_2 = embed_info[2] - bits

                image[row, col][channel], image[row, col + 1][channel] = _change_difference(image[row, col][channel], image[row, col + 1][channel], difference, difference_2)
                message =  message[embed_info[0]:]
        row += 1
    return image

def decrypt(image_path, seed):
    image = cv2.imread(image_path)
    height, width, channels = image.shape
    width -= width % 2

    buffer = ""
    result = ""
    row = 0
    char = 'a'
    while row < height and char != '\0':
        for col in range(0, width, 2):
            for channel in range(channels):
                pix_1 = int(image[row, col][channel])
                pix_2 = int(image[row, col + 1][channel])

                difference = abs(pix_1-pix_2)

                embed_info = _embed_info_gen(difference)
                message_dec = embed_info[2] - difference

                message_bin = bin(message_dec)[2:].rjust(embed_info[0], "0")
                buffer = buffer + message_bin
                
                while len(buffer) >= 8 and char != '\0':
                    char = chr(int(buffer[:8], 2))
                    result = result + char
                    buffer = buffer[8:]
                if char == '\0':
                    break
        if char == '\0':
            break
        row += 1
    return result