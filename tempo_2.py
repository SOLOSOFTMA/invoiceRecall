import numpy as numpy
import cv2
import pytesseract
from PIL import Image

# img = cv2.imread('extracted_invoice.jpg')
img = Image.open('extracted_invoice.jpg')
a = pytesseract.image_to_string(img)

print (a)