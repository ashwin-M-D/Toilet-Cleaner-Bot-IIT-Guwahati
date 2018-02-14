# Import the required modules
from skimage.transform import pyramid_gaussian
from skimage.io import imread
from skimage.feature import hog
from sklearn.externals import joblib
from skimage.transform import rescale
import cv2
import argparse as ap
from nms import nms
from config import *
import sys
import time
import numpy as np
import serial
import warnings
import serial.tools.list_ports
import os, signal

def sliding_window(image, window_size, step_size):
    '''
    This function returns a patch of the input image `image` of size equal
    to `window_size`. The first image returned top-left co-ordinates (0, 0) 
    and are increment in both x and y directions by the `step_size` supplied.
    So, the input parameters are -
    * `image` - Input Image
    * `window_size` - Size of Sliding Window
    * `step_size` - Incremented Size of Window

    The function returns a tuple -
    (x, y, im_window)
    where
    * x is the top-left x co-ordinate
    * y is the top-left y co-ordinate
    * im_window is the sliding window image
    '''
    for y in xrange(0, image.shape[0], step_size[1]):
        for x in xrange(0, image.shape[1], step_size[0]):
            yield (x, y, image[y:y + window_size[1], x:x + window_size[0]])

	

if __name__ == "__main__":
    # Parse the command line arguments
    parser = ap.ArgumentParser()
    #parser.add_argument('-i', "--image", help="Path to the test image", required=True)
    parser.add_argument('-d','--downscale', help="Downscale ratio", default=2,
            type=int)
    parser.add_argument('-v', '--visualize', help="Visualize the sliding window",
            action="store_true")
    args = vars(parser.parse_args())



while(True) :
    	# Read the image
    	#im = imread(args["image"], as_grey=True)
    	cap = cv2.VideoCapture(0)
    	ret, frame = cap.read()

    	# Our operations on the frame come here
    	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    	im = cv2.resize(gray, (0,0), fx=1, fy=1) 
    

    	min_wdw_sz = (360, 360)
    	step_size = (100, 100)
    	downscale = args['downscale']
    	visualize_det = args['visualize']

    	# Load the classifier
    	clf = joblib.load(model_path)
	
    	# List to store the detections
    	detections = []
    	# The current scale of the image
    	scale = 0
    	# Downscale the image and iterate
    	for im_scaled in pyramid_gaussian(im, downscale=downscale):
    	    # This list contains detections at the current scale
    	    cd = []
    	    # If the width or height of the scaled image is less than
    	    # the width or height of the window, then end the iterations.
    	    if im_scaled.shape[0] < min_wdw_sz[1] or im_scaled.shape[1] < min_wdw_sz[0]:
    	        break
    	    for (x, y, im_window) in sliding_window(im_scaled, min_wdw_sz, step_size):
    	        if im_window.shape[0] != min_wdw_sz[1] or im_window.shape[1] != min_wdw_sz[0]:
    	            continue
    	        # Calculate the HOG features
    	        fd = hog(im_window, orientations, pixels_per_cell, cells_per_block)
		fd = fd.reshape(1, -1)
        	print fd.shape
        	pred = clf.predict(fd)
        	if pred == 1:
        	        print  "Detection:: Location -> ({}, {})".format(x, y)
        	        print "Scale ->  {} | Confidence Score {} \n".format(scale,clf.decision_function(fd))
        	        detections.append((x, y, clf.decision_function(fd),
        	            int(min_wdw_sz[0]*(downscale**scale)),
        	            int(min_wdw_sz[1]*(downscale**scale))))
        	        cd.append(detections[-1])
        	# Move the the next scale
        	scale+=1
	
	clone = im.copy()

    	# Perform Non Maxima Suppression
    	detections = nms(detections, threshold)
    	i=0
    	# Display the results after performing NMS
    	for (x_tl, y_tl, _, w, h) in detections:
    	    # Draw the detections
		i=i+1
        	cv2.rectangle(clone, (x_tl, y_tl), (x_tl+w,y_tl+h), (0, 0, 0), thickness=2)
    	cv2.imshow("Final Detections after applying NMS", clone)
    	cv2.waitKey()
    	cap.release()
	cv2.destroyAllWindows()

	#hog completed go to tracking
	
	if i!=1	:
		continue
	elif i==1 :
		print(x_tl)
		print(y_tl)
		(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
		 
		# Set up tracker.																																																							
		# Instead of MIL, you can also use
		 
		tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
		tracker_type = tracker_types[2]
	 
		if int(minor_ver) < 3:
		    	tracker = cv2.Tracker_create(tracker_type)
		else:
		        if tracker_type == 'BOOSTING':
		            tracker = cv2.TrackerBoosting_create()																																																																																																																																																																				
		        if tracker_type == 'MIL':
		            tracker = cv2.TrackerMIL_create()
		        if tracker_type == 'KCF':
		            tracker = cv2.TrackerKCF_create()
		        if tracker_type == 'TLD':
		            tracker = cv2.TrackerTLD_create()
		        if tracker_type == 'MEDIANFLOW':
		            tracker = cv2.TrackerMedianFlow_create()
		        if tracker_type == 'GOTURN':
		            tracker = cv2.TrackerGOTURN_create()
		
		# Read video
		video = cv2.VideoCapture(0)
	 	
		# Exit if video not opened.
		if not video.isOpened():
		        print "Could not open video"
		        sys.exit()
		 
		    # Read first frame.
		ok, frame = video.read()
		if not ok:
		        print 'Cannot read video file'
		        sys.exit()
		     
		# Define an initial bounding box
		bbox = (x_tl, y_tl, 360, 360)
		 
		# Initialize tracker with first frame and bounding box
		ok = tracker.init(frame, bbox)
		
		while True:
	        # Read a new frame
		        ok, frame = video.read()
			#frame = cv2.resize(framei, (0,0), fx=1, fy=1)
		        if not ok:
		        	break
		         
		        # Start timer
		        timer = cv2.getTickCount()
		 
		        # Update tracker
		        ok, bbox = tracker.update(frame)
		 
		        # Calculate Frames per second (FPS)
		        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
		 
		        # Draw bounding box
		        if ok:
		            	# Tracking success
		            	p1 = (int(bbox[0]), int(bbox[1]))
		            	p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
		            	cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
		        else :
		            	# Tracking failure
		            	cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,	(0,0,255),2)
				cv2.imshow("Tracking", frame)
				time.sleep(1)
				video.release()
				cv2.destroyAllWindows()
				continue
	 
		        # Display tracker type on frame
		        cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
	     
		        # Display FPS on frame
		        cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
		 	
			x1 =  (int(bbox[0])+180)
			y1 =  (int(bbox[1])+180)
			
			#c = str(s.readline())
			#s.flushInput()			
			c=0

			cv2.circle(frame, (x1, y1), 7, (255, 255, 255), -1)
			cv2.putText(frame, "center of comod", (x1 - 20, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
			
			cv2.circle(frame, ((frame.shape[1]/2), (frame.shape[0]/2)), 7, (255, 255, 255), -1)
			cv2.putText(frame, "center of frame", (((frame.shape[1]/2) - 20), ((frame.shape[0]/2) - 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
			
			x = (frame.shape[1]/2) - (int(bbox[0])+180)
			y = (frame.shape[0]/2) - (int(bbox[1])+180)

			st = "st"
			c=0

			if x<-50 :
				st = "r."+str(-x)+";"
			elif x>50 :
				st = "l."+str(x)+";"
						
			elif c == 1 :
				st = "c.1;"
			else :
				st = "f.0;"

			
			print(st)

		        # Display result
		        cv2.imshow("Tracking", frame)
	 		
			
			
		        # Exit if ESC pressed
		        k = cv2.waitKey(1) & 0xff
		        if k == 27 : 
				cv2.destroyAllWindows()
				video.release()			
				break
	
