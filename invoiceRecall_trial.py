import cv2
from collections import deque
import numpy as np
import requests
import json
from pprint import pprint
import sqlite3
import time
import datetime
import datefinder

# style.use('fivethirtyeight')

mouseX = None
mouseY = None
topLeft = None
topRight = None
bottomLeft = None
bottomRight = None
invoice = None



def jsonProcessing():
	test_file = ocr_space_file(filename='extracted_invoice.jpg', language='eng')
	data = json.loads(test_file)

	staticZero = 0
	itemCost_item = []
	initText = data['ParsedResults'][staticZero]['ParsedText']
	# pprint (initText)
	for index, line in enumerate(data['ParsedResults'][staticZero]['TextOverlay']['Lines']):
		stri = data['ParsedResults'][staticZero]['TextOverlay']['Lines'][index]['Words'][staticZero]['WordText']
		chars = set('0123456789$,.')
		if all((c in chars) for c in stri):
			topDist = data['ParsedResults'][staticZero]['TextOverlay']['Lines'][index]['Words'][staticZero]['Top']
			for index2, line2 in enumerate(data['ParsedResults'][staticZero]['TextOverlay']['Lines']):
				tempTop = data['ParsedResults'][staticZero]['TextOverlay']['Lines'][index2]['Words'][staticZero]['Top']
				stri2 = data['ParsedResults'][staticZero]['TextOverlay']['Lines'][index2]['Words'][staticZero]['WordText']
				if (topDist-15)< tempTop <(topDist+15) and stri2 != stri and len(stri)<10:
	#                 print ("lenstri stri1:", len(stri))
					if all((d in chars) for d in stri2):
						pass
					else:
						# print (stri, stri2)
						itemCost_item.append([stri, stri2])
	
	finITEM = []
	for index, x in enumerate(itemCost_item):
	#     print (x[1])
		unique = True
		for y in range(index+1,len(itemCost_item)):
			if x[1] == itemCost_item[y][1]:
				unique = False
		if unique == True:
			finITEM.append(x)

	# print (finITEM)


	jargon = initText.splitlines()
	for y in finITEM:
		for x in jargon:
			if y[1] in x:
				# print (x)
				y[1] = x
				break

	# print (finITEM)

	finTotal = []
	for x in finITEM:
		if 'total' in x[1].lower():
			# print (x)
			finTotal = x

	dateFound = False
	invoiceDate = None
	for x in jargon:
		if dateFound == True:
			break
		match = datefinder.find_dates(x, strict=True)
		for m in match:
			# print (m)
			invoiceDate = m
			dateFound = True


	invoiceTo = ''
	for index, x in enumerate(jargon):
		if 'buyer' in x.lower() or 'bill to' in x.lower():
			for i in range(5):
				# print (jargon[index+i])
				invoiceTo = invoiceTo + (jargon[index+i])
			break

	invoiceFrom = ''
	for i in range(3):
	#     print (jargon[i])
		try:
			invoiceFrom = invoiceFrom + jargon[i]
		except:
			pass

	return invoiceFrom, invoiceTo, invoiceDate, finTotal, finITEM 



def ocr_space_file(filename, overlay=True, api_key='714dc0c1c888957', language='eng'):
	""" OCR.space API request with local file.
			Python3.5 - not tested on 2.7
	:param filename: Your file path & name.
	:param overlay: Is OCR.space overlay required in your response.
									Defaults to False.
	:param api_key: OCR.space API key.
									Defaults to 'helloworld'.
	:param language: Language code to be used in OCR.
									List of available language codes can be found on https://ocr.space/OCRAPI
									Defaults to 'en'.
	:return: Result in JSON format.
	"""

	payload = {'isOverlayRequired': overlay,
						 'apikey': api_key,
						 'language': language,
						 }
	with open(filename, 'rb') as f:
			r = requests.post('https://api.ocr.space/parse/image',
												files={filename: f},
												data=payload,
												)
	return r.content.decode()


def stretchInvoice(img, Rect_Contour):
	img_height, img_width = img.shape[:2]
	pts1 = np.float32([Rect_Contour[1], Rect_Contour[2], Rect_Contour[3], Rect_Contour[0]])
	# pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])
	pts2 = np.float32([[0,0],[0,2600],[1950,2600],[1950,0]])
	M = cv2.getPerspectiveTransform(pts1, pts2)
	invoice = cv2.warpPerspective(img, M, (1950, 2600))
	# cv2.imshow('img', img)
	# print (Rect_Contour[0][0][0], Rect_Contour[0][0][1], Rect_Contour[1][0][0])
	# cv2.circle(img, (Rect_Contour[0][0][0],Rect_Contour[0][0][1]), 10, (0,255,0), -1)
	# cv2.circle(img, (Rect_Contour[1][0][0],Rect_Contour[1][0][1]), 10, (0,255,0), -1)
	# cv2.circle(img, (Rect_Contour[2][0][0],Rect_Contour[2][0][1]), 10, (0,255,0), -1)
	# cv2.circle(img, (Rect_Contour[3][0][0],Rect_Contour[3][0][1]), 10, (0,255,0), -1)

	# cv2.imshow('img', img)
	# cv2.waitKey(0)
	cv2.imwrite('extracted_invoice.jpg', invoice) #dont mess with this
	return invoice


def draw_circle(event,x,y,flags,param):
	global mouseX, mouseY
	if event == cv2.EVENT_LBUTTONDBLCLK:
		mouseX,mouseY = x,y
		# cv2.circle(img,(x,y),100,(255,0,0),-1)


def locateOctaPad():
	global mouseX, mouseY, topLeft, topRight, bottomLeft, bottomRight

	image_height, image_width = invoice.shape[:2]

	invoice_small = cv2.resize(invoice, (450, 600))
	cv2.namedWindow('invoice', cv2.WINDOW_NORMAL)
	cv2.setMouseCallback('invoice',draw_circle)
	hsvImage = cv2.cvtColor(invoice, cv2.COLOR_BGR2HSV)
	coordinatesLocated = False
	while not(coordinatesLocated):
		cv2.imshow("invoice", invoice)
		cv2.resizeWindow("invoice", 450,600)
		k = cv2.waitKey(20) & 0xFF
		if k == 27:
			break
		elif k == ord('i'):
			topLeft = [mouseX,mouseY]
			print (topLeft)
			# print hsvImage[mouseY, mouseX]
		elif k == ord('o'):
			topRight = [mouseX,mouseY]
			print (topRight)
		elif k == ord('k'):
			bottomLeft = [mouseX,mouseY]
			print (bottomLeft)
		elif k == ord('l'):
			bottomRight = [mouseX,mouseY]
			print (bottomRight)
		elif k == ord('q'):
			coordinatesLocated = True
	# Approx_Rect_Countour = deque([[topLeft], [bottomLeft], [bottomRight], [topRight]])
	
	# topLeft = [topLeft[0]*(4.333), topLeft[1]*(4.333)]
	# topRight = [topRight[0]*(4.333), topRight[1]*(4.333)]
	# bottomLeft = [bottomLeft[0]*(4.333), bottomLeft[1]*(4.333)]
	# bottomRight = [bottomRight[0]*(4.333), bottomRight[1]*(4.333)]

	Approx_Rect_Countour = np.array([[topRight], [topLeft], [bottomLeft], [bottomRight]], dtype=np.int32)
	return Approx_Rect_Countour
	# topLeft, topRight, bottomLeft, bottomRight = [35, 39], [148, 32], [13, 108], [165, 104]


def imgPreProcess(img):
	mod_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	mod_img = cv2.GaussianBlur(mod_img,(5,5),0)
	mod_img = cv2.adaptiveThreshold(mod_img,255,1,1,19,5)
	return mod_img


def findInvoice(mod_img):
	temp_image = mod_img.copy()
	_, Contours, _ = cv2.findContours(temp_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	#OGimg = cv2.cvtColor(Temp_Image,cv2.COLOR_GRAY2RGB)
	#cv2.drawContours(OGimg,Contours,-1,(0,255,0),1)
	#cv2.imshow("mod_img.png", OGimg)
	###Find the contours in the image
	###cv2.findContours(image, mode, method[, contours[, hierarchy[, offset]]])
	###(image) ~input binary image
	###Refer the link below for more info
	##http://docs.opencv.org/2.4/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html#findcontours
	Required_Rect_Contour = None
	Required_Contour_Area = 0
	for Contour in Contours:
		Contour_Area = cv2.contourArea(Contour)
		###Calculates the area enclosed by the vector of 2D points denoted by 
		## the variable Contour
		if Contour_Area > 500:
			if Contour_Area > Required_Contour_Area:
				Required_Contour_Area = Contour_Area
				Required_Rect_Contour = Contour
	###Code for finding out the largest contour (on the basis of area)
	Perimeter_of_Contour = cv2.arcLength(Required_Rect_Contour, True)
	###Calculates a contour perimeter or a curve length
	###cv2.arcLength(curve, closed)
	###(curve) ~Input vector of 2D points
	###(closed) ~Flag indicating whether the curve is closed or not
	Temp_Rect_Countour = cv2.approxPolyDP(Required_Rect_Contour, 0.05*Perimeter_of_Contour, True)
	global invoice
	cv2.drawContours(invoice,[Temp_Rect_Countour],-1,(0,255,0),2)
	# print (fourPointCountour)
	###Overwrites the black image with the area of the sudoku in white
	# mod_img = cv2.bitwise_and(mod_img,Mask)
	###Compares the mod_img and the Mask and blackens all parts 
	## of the image other than the sudoku
	#cv2.imshow('mod_img', mod_img)

	invoice_small = cv2.resize(invoice, (450, 600))
	cv2.imshow('invoice_small', invoice_small)

	print ("Was the document identified correctly (y/n)? : ")
	k = cv2.waitKey(0) & 0xFF
	if k == ord('y'):
		cv2.destroyAllWindows()
	elif k == ord('n'):
		cv2.destroyAllWindows()
		print ("Double click on the four corners of the document and press 'i', 'o', 'k', 'l' respectively for top left, top right, bottom left and bottom right. Press 'q' when done!")
		Temp_Rect_Countour = locateOctaPad()
		cv2.destroyAllWindows()
	return mod_img, Temp_Rect_Countour


def main():
	NUM_OF_FILES = 1
	for i in range(NUM_OF_FILES):
		# Load the image
		# file_name = 'invoice_'+str(i+1)+'.jpg'
		file_name = 'invoice_1.jpg'
		global invoice
		img = cv2.imread(file_name)
		invoice = img.copy()
		img_height, img_width = img.shape[:2]

		mod_img = imgPreProcess(img)
		mod_img, cont = findInvoice(mod_img)
		# print (cont)
		mod_image = stretchInvoice(img, cont)

		cv2.destroyAllWindows()
		# test_file = ocr_space_file(filename='extracted_invoice.jpg', language='eng')
		# data = json.loads(test_file)


		invoiceFrom, invoiceTo, invoiceDate, finTotal, finITEM = jsonProcessing()
		print ('\n\n', invoiceFrom, '\n\n', invoiceTo, '\n\n', invoiceDate, '\n\n', finTotal, '\n\n', finITEM, '\n\n')

		# dBase(invoiceFrom, invoiceTo, invoiceDate, finTotal, finITEM)

		# cv2.imshow('mod_image', mod_image)


if __name__ == "__main__":
	main()