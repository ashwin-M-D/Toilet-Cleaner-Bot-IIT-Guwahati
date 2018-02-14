import cv2
import numpy as np
import imutils
import time
import sys
import serial
import warnings
import serial.tools.list_ports
import os, signal





arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description
]
if not arduino_ports:
    raise IOError("No Arduino found")
if len(arduino_ports) > 1:
    warnings.warn('Multiple Arduinos found - using the first')

#s = serial.Serial(arduino_ports[0], 9600) # takes the first arduino which ever is in the list

s = serial.Serial('/dev/ttyACM0', 9600)# have to automate this selection of port
s.flushInput()
s.flushOutput()





cap = cv2.VideoCapture(1)

while(1):
        _, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([84, 40 , 95])
        upper_green= np.array([104, 90, 185])
        mask = cv2.inRange(hsv, lower_green, upper_green)
	res = cv2.bitwise_and(frame,frame, mask= mask)
    
	gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)	
	thresh = cv2.threshold(blurred, 120, 255, cv2.THRESH_BINARY)[1]

	# find contours in the thresholded image
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	# loop over the contours
	c=l=0
	cX=frame.shape[0]
	cY=frame.shape[1]
	for i in cnts:
		k = cv2.contourArea(i)		
		c = i
		l = k

	if len(cnts) == 0 :
		cv2.imshow('image', frame)
		k = cv2.waitKey(10) & 0xFF 
		if k == 113 or k == 27:
	    		break
		continue


	for i in cnts:
		k = cv2.contourArea(i)		
		if k>l :
			c = i
			l = k
	

	if cv2.contourArea(c) > 0:
		# compute the center of the contour
		M = cv2.moments(c)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
	
		# draw the contour and center of the shape on the image
		# draw the contour and center of the shape on the image
		cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
		cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
		cv2.putText(frame, "center", (cX - 20, cY - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

		# show the image
		cv2.imshow('image', frame)
	else :
		cv2.imshow('image', frame)
	if cX > int((frame.shape[0])/2) :  #right
		print("right cX = "+str(cX)+"Center = "+str((frame.shape[0])/2))
		time.sleep(0.05)
		s.flushOutput()	
		s.write("l.50")
		while s.in_waiting==0 : time.sleep(0.001)

	elif cX < ((frame.shape[0])/2) :  #left
		print("left cX = "+str(cX)+"Center = "+str((frame.shape[0])/2))
                time.sleep(0.05)
		s.flushOutput()	
		s.write("r.40")
		while s.in_waiting==0 : time.sleep(0.001)

	else :
		print("centered")
                time.sleep(2)
		break
	k = cv2.waitKey(10) & 0xFF
        if k == 113 or k == 27:
                break
cv2.destroyAllWindows()
cap.release()
s.flushOutput()	
s.write("r.100")
while s.in_waiting==0 : time.sleep(0.001)
s.flushOutput()	
s.write("r.100")
while s.in_waiting==0 : time.sleep(0.001)
s.flushOutput()	
s.write("r.100")
while s.in_waiting==0 : time.sleep(0.001)
s.flushOutput()	
s.write("f.20000")
while s.in_waiting==0 : time.sleep(0.001)
time.sleep(20)
