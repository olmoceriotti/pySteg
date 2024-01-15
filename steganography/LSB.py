import cv2
def _text_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def encrypt(message, image_path, seed):
    message = _text_to_binary(message)
    image = cv2.imread(image_path)
    height, width, channels = image.shape
    index = 0
    if(len(message) > height*width*channels):
        print("Not enough space to embed message: change image or shorten the message")
        return None
    for x in range(width):
        for y in range(height):
            pixel = image[y, x]
            for channel in range(channels):
                if(index < len(message)):
                    pixel[channel] = pixel[channel] & ~1 | int(message[index])
                    index += 1
    return image

def decrypt(image_path, seed):
    message = ""
    char = ""
    message_retrieved = False
    image = cv2.imread(image_path)
    height, width, channels = image.shape
    for x in range(width):
        if(message_retrieved): 
            break
        for y in range(height):
            pixel = image[y, x]
            for channel in range(channels):
                LSB = bin(pixel[channel])[2:].zfill(8)[7]
                char += LSB
                if len(char) % 8 == 0:
                    newChar = chr(int(char, 2))
                    char = ""
                    if(newChar == '\0'):
                        print("message retrieved")
                        return message
                    else:
                        message += newChar