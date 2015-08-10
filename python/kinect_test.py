#import the necessary modules
import freenect
import cv
import cv2
import numpy as np
import frame_convert
import OSC
import json
import socket
import sys

class Blob:
    def __init__(self, avgx, avgy, avgz):
        self.x = avgx
        self.y = avgy
        self.z = 0
        self.w = 0
        self.h = 0

def change_depth(value):
    global current_depth
    current_depth = value

def change_threshold(value):
    global threshold
    threshold = value

def change_min_area(value):
    global min_area
    min_area = value

def change_bdelta(value):
    global bdelta
    bdelta = value

#function to get RGB image from kinect
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    return array
 
#function to get depth image from kinect
def get_depth():
    array,_ = freenect.sync_get_depth()
    array = array.astype(np.uint8)
    return array

    #return frame_convert.pretty_depth_cv(freenect.sync_get_depth())

iFrame = 1 
firstFrame = None
current_depth = 1
threshold = 50
min_area = 4000
bdelta = 50
blobs = {}

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
    ip = s.getsockname()[0]
    #ip = socket.gethostbyname(socket.gethostname())
    c = OSC.OSCClient()
    #c.connect(('192.168.1.129', 7400))   # connect to Max
    #c.connect(('192.168.1.255', 7400))   # connect to Max
    #c.connect(('255.255.255.255', 7400))   # connect to Max
    while 1:
        iFrame = iFrame + 1
        #get a frame from RGB camera
        #frame = get_video()
        #get a frame from depth sensor
        depth = get_depth()
        depth_o = depth.copy()
        #depth = cv2.resize(depth, (0,0), fx=0.25, fy=0.25)

        depth = 255 * np.logical_and(depth >= current_depth - threshold,
                                     depth <= current_depth + threshold)
        depth = depth.astype(np.uint8)

        #if firstFrame is None:
        #    firstFrame = depth
        #    continue

        # compute the absolute difference between the current frame and
        # first frame
        #frameDelta = cv2.absdiff(firstFrame, depth)
        #thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        #thresh = cv2.dilate(thresh, None, iterations=2)

        #(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        cnts = cv2.findContours(depth.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        new_blobs = {}

        # loop over the contours
        for cnt in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(cnt) < min_area:
                continue

            #Finding centroids of cnt and draw a circle there
            M = cv2.moments(cnt)
            cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cz = depth_o[cy][cx]
            new_id = -1
            
            for idx,blob in blobs.items():
                if blob.x < (cx + bdelta) and blob.x > (cx - bdelta) and blob.y < (cy + bdelta) and blob.y > (cy - bdelta):
                    new_blobs[idx] = Blob((int(blob.x) + cx)/2, (int(blob.y) + cy)/2, (int(blob.z) + cz)/2)
                    new_id = idx
                    break

            if new_id == -1:
                new_id = 1
                blob_ids = blobs.keys()
                while True:
                    if new_id in blob_ids:
                        new_id = new_id + 1
                        continue
                    else:
                        new_blobs[new_id] = Blob(cx, cy, cz)
                        break


            #cv2.circle(depth,(cx,cy),10,0,-1)
            cv2.putText(depth,str(new_id),(cx,cy),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,0))

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.rectangle(depth, (x, y), (x + w, y + h), (255, 255, 255), 2)
            new_blobs[new_id].w = w
            new_blobs[new_id].h = h
            #print depth_o.shape
            new_blobs[new_id].z = depth_o[cy][cx]

        blobs = new_blobs

        if bool(blobs):
            for idx,blob in blobs.items():
                oscmsg = OSC.OSCMessage()
                oscmsg.setAddress("/blob")
                oscmsg.append(idx)
                oscmsg.append(float(blob.x) / 640.0)
                oscmsg.append(float(blob.y) / 480.0)
                oscmsg.append(float(blob.w) / 640.0)
                oscmsg.append(float(blob.h) / 480.0)
                oscmsg.append(blob.z)
                oscmsg.append(ip)
                try:
                    c.sendtobroadcast(oscmsg, ('192.168.1.255', 7400))
                except OSC.OSCClientError:
                    print 'Failed to send packet'

        fi = open('/home/pi/web/input.txt', 'r')
        try:
            params = json.load(fi)
            current_depth = int(params['start_depth'])
            threshold = int(params['end_depth'])
            min_area = int(params['min_area'])
            bdelta = int(params['blob_delta'])
        except ValueError:
            pass
        fi.close()


        #display RGB image
        #cv2.imshow('RGB image',frame)
        #display depth image
        if len(sys.argv) > 2:
            cv2.imshow('Depth',depth)
            cv.CreateTrackbar('start_depth', 'Depth', current_depth, 2048, change_depth)
            cv.CreateTrackbar('end_depth', 'Depth', threshold,     500,  change_threshold)
            cv.CreateTrackbar('min_area',  'Depth', min_area, 50000, change_min_area)
            cv.CreateTrackbar('blob_delta','Depth', bdelta, 100, change_bdelta)

        cv2.imwrite('/home/pi/web/public/images/foo.png', depth)

        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()