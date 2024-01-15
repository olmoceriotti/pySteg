import matplotlib.pyplot as plt
import subprocess
import matplotlib.image as mpimg
import numpy as np

def plot(image1, image2, image3, save_path):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    ax1.imshow(image1)
    ax1.set_title('Cover Image')
    ax1.axis('off')
    ax2.imshow(image2)
    ax2.set_title('Stego Image')
    ax2.axis('off')
    ax3.imshow(image3)
    ax3.set_title('Difference')
    ax3.axis('off')
    plt.savefig(save_path)
    plt.show()

command = "python3 main.py enc https://en.wikipedia.org/wiki/Steganography -i \"This is a test message\" -a QR -Qv 6"

result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

image1 = mpimg.imread("original_qr_code.png")
image2 = mpimg.imread("flipped_pixels.png")
image3 = mpimg.imread("output.png")
plot(image1, image2,image3, "QR_comparison.png")