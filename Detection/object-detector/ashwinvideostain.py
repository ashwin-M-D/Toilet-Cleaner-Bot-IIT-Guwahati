# import the necessary packages
import imutils
import cv2
import numpy as np
import time
import sys
import numpy as np
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
s = serial.Serial(arduino_ports[0],9600)# have to automate this selection of port
s.write('a')
time.sleep(5)
s.write('a')
time.sleep(5)
s.flushInput()
s.flushOutput()

rtncmd = 'ttt'
#condition paramenters
lt_area = 500
ut_area = 2500
kp = 0.5
edgelinecancellation = 0 #1 to enable and 0 to disable  
while(1):
	if rtncmd == 'danger\r\n' :
		s.write('a')
		while s.inWaiting() ==0 : time.sleep(0.001)
		rtncmd = s.readline()
		continue
	cap = cv2.VideoCapture(1)
	ret, frame=cap.read()
	gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	ret,thresh=cv2.threshold(blurred,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)	
	#thresh = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
	#thresh=cv2.bitwise_not(thresh)
	# noise removal
	kernel = np.ones((3,3),np.uint8)
	opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

	
	cv2.imshow("thresh",thresh)
	# find contours in the thresholded image
	cnts = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	c=l=0
	nX = None
	nY = None

	if len(cnts) == 0 :
		cv2.imshow('image', frame)

		k = cv2.waitKey(1) & 0xFF 
		if k == 113 or k == 27:
	    		break
		continue

	# for i in cnts:
	# 	k = cv2.contourArea(i)		
	# 	if k>l  :
	# 		#print k
	# 		c = i
	# 		l = k

	
	# loop over the contours
	for i in cnts:
		k = cv2.contourArea(i)
		if k>l and k<ut_area and k> lt_area :
			# compute the center of the contour
			M = cv2.moments(i)
			#print(M)
			#print ('hello')
			#time.sleep(0.001)
			if M["m00"] != 0:
				
				cX = int(M["m10"] / M["m00"])
				cY = int(M["m01"] / M["m00"])
				if(nY == None or nY <cY):					
					nX=cX
					nY=cY
					c = i
					# draw the contour and center of the shape on the image
				cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
				cv2.circle(frame, (nX, nY), 7, (255, 255, 255), -1)
	if(nX == None):
		s.write("b.1000")
		time.sleep(1)
		s.write("l.100")	
						
	if( edgelinecancellation !=1 and nX != None):
		
		print ('(nX,nY) = ' + str(nX) +' & '+str(nY) + '\n')
		pwm = kp*(nX -  (frame.shape[0]/2))
		print ('pwm is '+ str(pwm)  )
		
		if pwm <75 and pwm > -75:
			# s.flushOutput()
			s.flushInput()
			s.write("f.5000")
			time.sleep(5)
			while s.inWaiting() ==0 : time.sleep(0.001)
			rtncmd = s.readline()
			#s.flushInput()
			print rtncmd
			if rtncmd == "danger\r\n":
				# s.flushOutput()
				# s.flushInput()
				s.write('a')
				while s.inWaiting() ==0 : time.sleep(0.001)
				rtncmd = s.readline()
				continue

		elif pwm > 75:
			s.write("r.100")
			print("r.pwm")
			time.sleep(0.3)
			while s.inWaiting() ==0 : time.sleep(0.001)
			rtncmd = s.readline()
			#s.flushInput()
			print rtncmd
			if rtncmd == "danger\r\n":
				# s.flushOutput()
				# s.flushInput()
				s.write('a')
				continue

		elif pwm < -75:
			s.write("l.100")
			print("l.pwm")
			time.sleep(0.3)
			while s.inWaiting() ==0 : time.sleep(0.001)
			rtncmd = s.readline()
			#s.flushInput()
			print rtncmd
			if rtncmd == "danger\r\n":
				# s.flushOutput()
				# s.flushInput()
				s.write('a')
				while s.inWaiting() ==0 : time.sleep(0.001)
				rtncmd = s.readline()
				continue

	cv2.imshow("Image", frame)
	cv2.waitKey(500)
	cv2.destroyAllWindows()
	cap.release()

	# k = cv2.waitKey(1) & 0xFF
	# if k == 113 or k == 27:
	#     break
cv2.destroyAllWindows()
cap.release()
					




		#s.flushOutput()
		
		#s.write('(nX,nY) = ' + str(nX) +' & '+str(nY)+ ' \n')
				#time.sleep(0.005)
				#break
	#cv2.putText(image, "center", (cX - 20, cY - 20),
	#	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

	# show the image
	#line above -neglect
			# elif (edgelinecancellation ==1):
			# 	edges = cv2.Canny(gray,50,150,apertureSize = 3)
			# 	cv2.imshow("Canny", edges)
			# 	# minLineLength = 100
			# 	# maxLineGap = 10
			# 	# lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
			# 	# if lines != None:	
			# 	# 	for x1,y1,x2,y2 in lines[0]:
			# 	# 	    cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)

			# 	lines = cv2.HoughLines(edges,1,np.pi/180,200)
			# 	if lines != None:
			# 		for rho,theta in lines[0]:
			# 			#time.sleep(0.05)
			# 			a = np.cos(theta)
			# 			b = np.sin(theta)
			# 			#print "cos-theta is =" + str (abs(a))
			# 			if (abs(a) < 0.75 ):
			# 				x0 = a*rho
			# 				y0 = b*rho
			# 				x1 = int(x0 + 1000*(-b))
			# 				y1 = int(y0 + 1000*(a))
			# 				x2 = int(x0 - 1000*(-b))
			# 				y2 = int(y0 - 1000*(a))
			# 				cv2.line(frame,(x1,y1),(x2,y2),(255,0,0),2)
			# 				sideconst =  (x2-x1)*(nY-y1) - (y2-y1)*(nX-x1)
			# 				if (sideconst< 0 ):
			# 					continue
			# 				else:
			# 					#print (cX,cY)
			# 					cv2.circle(frame, (nX, nY), 15, (0, 0, 255), -1)
			# 					print ('(nX,nY) = ' + str(nX) +' & '+str(nY))
			# 					s.flushOutput()
			# 					s.write('(nX,nY) = ' + str(nX) +' & '+str(nY))
			# 					break
			# 					break
			# 					#time.sleep(0.005)
			# 	else:
			# 		print ('(nX,nY) = ' + str(nX) +' & '+str(nY))
			# 		s.flushOutput()
			# 		s.write('(nX,nY) = ' + str(nX) +' & '+str(nY))
			# 		break
			# 		time.sleep(0.005)
	
