<div align="center">
<!-- Title: -->
  <a href="">
    <img src="Resources/github/pysteg-high-resolution-logo-transparent.png" height="100">
  </a>
  <h1>A steganography tool written in Python</h1>
<!-- Short description: -->
</div>

PySteg is a tool in Python capable of hiding and extracting information in different medias.
This tool can perform 3 types of spatial domain steganography on digital images and embed small messages inside QR codes.

The usage is designed to be used as a normal command line program. For each usage is necessary to specify two things: the mode and the cover media. There are two modes: encoding and decoding. In encoding mode is required to also specify the message to embed. To do so the available option is  ```-in```. It accepts both strings and paths to files. The cover media should always be a PNG image except if the selected algorithm is QR, in that case a piece of text will be necessary.
Here is a list of all available options:

1. ```-in``` for specifying the input in encoding mode
2. ```-out```for specifying the output file in decoding mode
3. ```-o``` for overwriting the orignal cover image with the stego image
4. ```-a``` for choosing the algorithm to perform steganography with. LSB, PVD and RPP are available to hide information in digital images and QR for doing the same with QR codes. The default algorithm is LSB.
5. ```-s``` for specifying the seed needed to perform RPP encoding and decoding. There is no default value.
6. ```-Qv``` for specifying the minimum QR code version where your message is going to be encoded.
7. ```-d``` for requesting the program to generate difference images to show where pixels have been changed in the stego image.
8. ```-b``` for specifying the need to decode/encode the file to embed or to extract in Base64. This option is needed for messages that are not text.

Here is some code snippets to test the tool: \
```python3 main.py enc Resources/test_cover.png -in Resources/test_file_message.png -b``` \
```python3 main.py dec Resources/output.png -out Resources/test_result.png -b```

```python3 main.py enc Resources/test_cover.png -in Resources/test_text.txt -a PVD -d``` \
```python3 main.py dec Resources/output.png -a PVD -out test_result.txt```

```python3 main.py enc Resources/test_cover.png -in "This is the payload" -a RPP -s 123456``` \
```python3 main.py dec Resources/output.png -a RPP -s 123456 -out test_result.txt```

```python3 main.py enc https://github.com/olmoceriotti/pySteg -in "Secret message" -Qv 5 -a QR``` \
```python3 main.py dec output.png -a QR -out test_result.txt```

## The steganography techniques

The three techniques chosen for this project are Least Significant Bit, Pixel Value Differencing and Random Pixel Positioning. All three of this techniques are part of the spatial domain section of steganography. Here is a simple explanation of these three techniques.

LSB steganography is based on the concept that the human eye can't perceive the complete range of color that digital images can represent and slight changes in the colors can go completly unnoticed by the human eye. The techniques is then based on changing the last bit that composes each of the channel of every pixel with one of the bit that composes the secret message. The extraction procedure goes as expected by traversing the image in the same direction and collecting the hidden bits.

PVD steganography is based on the same concept as LSB but with an increased and variable number of embedded bits for each couple of pixels. The number of bits to embed is chosen by taking the base 2 logarithm of the difference between the two closest to the difference perfect squares. Than a new difference is calculated and split between the two pixels accounting for overflow. In the extraction process when the couple of pixels is going to be taken in account the difference between them will be processed in reverse to extract the message bits.

RPP steganographys embeds 8 bit of message in every bit of the image, 3 in the red channel, 3 in the green channel and 2 in the blue channel. The radical difference is the direction of embedding. RPP uses a pseudo random number generator (PRNG) to determine in which pixels the information is going to be embedded. Once the pixel is decided, the bits are embedded in the last 2 or 3, depending on the channel, LSBs by XORing them with a randomly decided MSB decided by using the same PRNG. The extraction is perfomed by using the same seed used in the embedding. This way the same extact actions are performed in the same order and the message is then extracted.

## QR Codes

The QR code steganography is based on the notion that QR codes can still be readable  by scanners even if they present a certain numbers of errors or damage. This way, it's possible to change some of the square that composes them in order to hide a message in an innocent looking QR code. The embedding is done by converting the message in a black and white image that's gonna act as a mask with a normal generated QR Code. After the normal QR is masked the resulting QR code is going to be readable thanks to the error correction and the message is going to be hidden. The extraction process is based on the same principle. A QR Code with the same version  and the same exact public message of the stego QR Code is going to be generated and the difference between the two is going to be equal to the masking image used in the embedding process. At that point it's sufficient to convert the image back into the message to successfully read it. The QR code procedure saves every image generated in the computation. The final result is saved inside "output.png" while the image "flipped_pixels.png" is the mask used to generate the image. "Original_qr_code.png" is the QR code without any hidden message.

## Constraints

The only cover image format tested and succesfully supported is standard PNG images.
The messages can be as big as the image is capable to contain, there is a mechanism to check if the message is too long for RPP and LSB but not for PVD, given the fact that to calculate the embedding capacity of an image would be going to require double the computation.
The RPP algorithm given the fact that has to generate unique numbers can be slow when given large messages.
QR Codes are suitable for hiding only small text messages.
At the end of every QR code creation a reader is invoked to check if the generated code is readable and if not it suggests possible solutions.

### Requirements

The following libraries were used inside the project:

1. cv2
2. qrcode
3. numpy
4. pyzbar
5. skimage

To use pzybar, zbar needs to be installed on the computer  with ```sudo apt-get install libzbar0``` and for using cv2, opencv may be needed. Numpy and skimage are needed only to generate difference images, to avoid installing them avoid to use the ```-d``` flag.
