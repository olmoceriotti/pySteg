#!/usr/local/bin/python3

import argparse
import os
import cv2
from steganography.LSB import encrypt as lsb_encrypt, decrypt as lsb_decrypt
from steganography.PVD import encrypt as pvd_encrypt, decrypt as pvd_decrypt
from steganography.RND import encrypt as rnd_encrypt, decrypt as rnd_decrypt
from steganography.QR import encrypt as qr_encrypt, decrypt as qr_decrypt
from steganography.utils import difference

algorithm_functions = {
    'LSB': (lsb_encrypt, lsb_decrypt),
    'PVD': (pvd_encrypt, pvd_decrypt),
    'RPP': (rnd_encrypt, rnd_decrypt), 
}

parser = argparse.ArgumentParser(description='A utility for image steganography.')
parser.add_argument('mode', choices=['enc', 'dec'])
parser.add_argument('cover', type=str, help="Path to the cover image or cover text for QR")
parser.add_argument('-i', '--input', type=str, help="Message to embed or path to textfile")
parser.add_argument('-o', '--overwrite', action='store_true', help="Overwrite the original image")
parser.add_argument('-a', '--algorithm', choices=["LSB", "PVD", "RPP", "QR"], help="Algorithm used, default LSB")
parser.add_argument('-s', '--seed', type=str, help="Seed for the random number generator used in RPP steg")
parser.add_argument('-Qv', '--QR_version', type=int, help="Minimum requested QR code version")
parser.add_argument('-d','--difference', action='store_true', help="Generate a difference image")
parser.add_argument('-e', '--encryption', nargs='?', const=True, default=False, help="Perform encryption with Fernet")

args = parser.parse_args()
print(args)

def path_check(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            return True
    return False

def main():
    if args.algorithm == "QR":
        if args.mode == "enc":
            image_with_message = qr_encrypt(args.cover, args.input, version=args.QR_version)
            if args.overwrite:  
                print("Impossible to overwrite non existing file!")
            cv2.imwrite("output.png", image_with_message)  
        else:
            result = qr_decrypt(args.cover)
            print(result)
    else:
        if path_check(args.cover):
            if args.algorithm in algorithm_functions:
                encrypt, decrypt = algorithm_functions[args.algorithm]
            else:
                encrypt, decrypt = algorithm_functions["LSB"]

            if args.mode == "enc":
                print("Encrypting...")
                if args.input != None:
                    message = ""
                    if path_check(args.input):
                        with open(args.input, 'r') as file:
                            message = file.read()
                    else:
                        message = args.input
                    if args.encryption:
                        print("Encryption not yet available")
                    message = message + '\0'
                    original_image = None
                    if args.difference != None:
                        original_image = cv2.imread(args.cover)
                    image_with_message = encrypt(message=message, image_path=args.cover, seed = args.seed)
                    path = args.cover[:args.cover.rfind("/") + 1]

                    if args.overwrite != None:  
                        cv2.imwrite(path + "output.png", image_with_message)
                    else:
                        cv2.imwrite(args.cover, image_with_message)
                    if args.difference != None:
                        images = difference(original_image, image_with_message)
                        for img in images:
                            cv2.imwrite(path + img[0], img[1])  
                else:
                    print("Missing text to encrypt")
            else: 
                print("Decrypting...")
                result = decrypt(image_path=args.cover, seed=args.seed)
                print(result)
        else:
            print("Invalid image path: " + args.cover)

if __name__ == "__main__":
    main()