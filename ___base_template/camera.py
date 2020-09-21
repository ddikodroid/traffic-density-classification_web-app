# package opencv
import cv2, os, time, imutils, shutil, glob
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth

count = 0
keyframe = ''



class VideoCamera:
    # ambil video
    def __init__(self, method, filevideo, filequery):
        # self.cleanfile()
        self.RESIZE_RATIO = 0.5
        featureextraction = method
        self.filevideo = filevideo
        self.filequery = filequery

        if featureextraction == 'SIFT':
            self.algoritma = cv2.xfeatures2d.SIFT_create(nfeatures=2500, nOctaveLayers=10)
            index_params = dict(algorithm=1, trees=2)
            search_params = dict()
            self.matching = cv2.FlannBasedMatcher(index_params, search_params)
        elif featureextraction == 'SURF':
            self.algoritma = cv2.xfeatures2d.SURF_create()
            index_params = dict(algorithm=1, trees=2)
            search_params = dict()
            self.matching = cv2.FlannBasedMatcher(index_params, search_params)
        elif featureextraction == 'ORB':
            # algoritma ekstraksi fitur ORB
            self.algoritma = cv2.ORB_create(nfeatures=2500, scoreType=cv2.ORB_FAST_SCORE, nlevels=10, patchSize=20, edgeThreshold=5)
            # matching fitur BF Matcher dengan Hamming distance
            self.matching = cv2.BFMatcher(cv2.NORM_HAMMING2)
        
        print("Cetak data Video : ", self.filevideo)

        img = cv2.imread(self.filequery)  # citra query
        # resize citra query
        queryimg = imutils.resize(img, width=200, height=200)
        # konversi RGB to Grayscale
        self.imggray = cv2.cvtColor(queryimg, cv2.COLOR_BGR2GRAY)
        # keypoint dan descriptor citra query
        self.kp_image, self.desc_image = self.algoritma.detectAndCompute(self.imggray, None)
        
        self.video = cv2.VideoCapture(self.filevideo)
    
    # release video
    def stop(self):
        self.video.release()      

    def cleanfile(self):
        global count
        count = 0
    
    
    # ekstraksi video
    def get_frame(self):
        global count
        success, frameawal = self.video.read()
        if not success:
            img_break = "./templates/endVideo.jpg"
            imgbreak = cv2.imread(img_break)
            _, jpeg_break = cv2.imencode('.jpg', imgbreak)
            return success, jpeg_break.tobytes()
        frameori = cv2.resize(frameawal, None, fx=self.RESIZE_RATIO, \
                fy=self.RESIZE_RATIO) 
        
        count += 1
        
        ret, jpeg = cv2.imencode('.jpg', frameori)
        # if not ret:
        #     cv2.putText(frame,"Video has been stopped",(0,0),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1)
        return success, jpeg.tobytes()



