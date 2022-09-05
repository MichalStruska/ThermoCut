import numpy as np
from PIL import Image
import cv2
import glob, os
import pandas as pd
import sys
sys.path.append(r"/Users/michalstruska/Dropbox/Michal S/ThermoCutter/Python")
import ImageOperations as io
import scipy
from skimage.draw import line
from scipy.spatial import ConvexHull

class ImageEdit:
    def __init__(self, image_path, text_directory):
        self.text_directory = text_directory
        self.image_path = image_path
        self.mode = True
        self.image = cv2.imread(image_path)
        self.line_coordinates = []
        self.cut_line = []
        self.CreateWindow()
        self.EndlessCycle()
    
    def CreateWindow(self):
        height, width, channels = self.image.shape
        cv2.namedWindow('Window',cv2.WINDOW_NORMAL)
        
    
    def InteractiveDrawing(self,event,x,y,flags,param):
        global ix,iy,drawing, mode
        if event==cv2.EVENT_LBUTTONDOWN:
            drawing=True
        
        if event==cv2.EVENT_LBUTTONUP:
            if self.mode==True:
                cv2.circle(self.image,(x,y),1,(0,0,255),-1)
                if self.line_coordinates !=[]:
                    # cv2.line(self.image,(self.line_coordinates[-1][0],self.line_coordinates[-1][1]),
                    #          (x,y),color = (0, 125, 0, 100), thickness = 5)
                    
                    rr, cc = line(self.line_coordinates[-1][1], self.line_coordinates[-1][0], y, x)
                    self.image[rr, cc] = 1
                    
                    self.cut_line.append([rr,cc])
                    
                self.line_coordinates.append([x,y])
        if event==cv2.EVENT_RBUTTONDOWN:
            x,y=self.line_coordinates[0][0],self.line_coordinates[0][1]
            cv2.circle(self.image,(x,y),1,(0,0,255),-1)
            if self.line_coordinates !=[]:
                cv2.line(self.image,(self.line_coordinates[-1][0],self.line_coordinates[-1][1]), (x,y),
                         color = (0, 125, 0), thickness = 5)
            self.line_coordinates.append([x,y])
            drawing=False
            
    def DrawSegment(self):
        ['A','FA','H','N','S','T','TO']
        for segment in pripony1:
            side = self.GetEnd(segment)
            
            r = os.path.basename(self.image_path)
            s = os.path.splitext(r)[0]
            if s + '_' + segment + "_" + side + '.txt' in os.listdir(self.text_directory):
                mask = np.genfromtxt(os.path.join(self.text_directory,s + '_' + segment + "_" + side + '.txt'),delimiter='\t')
                mask_upright = io.RotateImageRight(mask)
                self.CreateOutline(mask_upright)
                # cv2.circle(mask,(240,320),280,1,thickness=-1)
                
                # res = cv2.bitwise_not(self.image,self.image,mask = np.int8(mask_outer))
                cv2.imshow('Window',self.image)
    
    def CreateOutline(self, shape):
        for i in np.arange(0,len(shape[:,1])):
                for j in np.arange(0,len(shape[1,:]) - 1):
                    if shape[i,j]==0 and shape[i,j+1]!=0:
                        self.image[i,j]=255
                    if shape[i,j]==0 and shape[i,j-1]!=0:
                        self.image[i,j]=255
        for i in np.arange(0,len(shape[:,1]) - 1):
                for j in np.arange(0,len(shape[1,:])):
                    if shape[i,j]==0 and shape[i+1,j]!=0:
                        self.image[i,j]=255
                    if shape[i,j]==0 and shape[i-1,j]!=0:
                        self.image[i,j]=255
    
    def GetEnd(self, segment):
        if segment in ['TO', 'N', 'FH']:
            return 'na'
        else:
            return 'R'
    
    def EndlessCycle(self):
        while(1):
            result = cv2.addWeighted(self.image, 0.5, self.image, 1 - 0.5, 0)
            cv2.imshow('Window',self.image)
            cv2.setMouseCallback('Window',self.InteractiveDrawing)
            k=cv2.waitKey(1)&0xFF
            
            if k == ord("p"):
                cv2.imshow('Window',self.image)
                
            if k==27:
                break


if __name__ == '__main__':
    png_file_path = r"/Users/michalstruska/Dropbox/Michal S/kamera"
    text_files_path = r'/Users/michalstruska/Dropbox/Michal S/kamera'
    missing_txt_files = []

    

    files = glob.glob(os.path.join(png_file_path,'*.png'))
    for file in files[0:1]:
        # im = Image.open(file)
        # im.show()
        image_test = cv2.imread(file)
        print(image_test)
        cv2.namedWindow('Window', cv2.WINDOW_NORMAL)
        cv2.imshow('Window',image_test)
        
        pripony1 = ['A','FA','H','N','S','T','TO']
        image_edit = ImageEdit(file, text_files_path)




