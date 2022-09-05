import numpy as np
from PIL import Image
import cv2
import glob, os
import pandas as pd
import sys
sys.path.append(r"C:\Users\Michal\ThermoCutter\Python")
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
        self.active_outline = []
        # self.CreateWindow()
        self.EndlessCycle()
    
    def CreateWindow(self):
        height, width, channels = self.image.shape
        cv2.namedWindow('Window',cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Window", int(width*1.5), int(height*1.5))
        cv2.imshow('Window',self.image)
    
    def FindCrossings(self):
        crossings = []
        for cutline_x,cutline_y in zip(self.cut_line[0][0], self.cut_line[0][1]):
            for outline_point in self.active_outline:
                if cutline_x == outline_point[0] and cutline_y == outline_point[1]:
                    crossings.append((cutline_x, cutline_y))
        return crossings    
            
    def DividePixels(self):
        print(self.FindCrossings())
    
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
            
    def CutSegment(self):
        self.DividePixels()
        
        # if event == cv.EVENT_MOUSEMOVE:
        #     if x
        
        
    def DrawSegment(self):
        pripony1 = ['A','FA','H','N','S','T','TO']
        segment = input("give segment:")
        # for segment in pripony1:
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
        self.active_outline = []
        for i in np.arange(0,len(shape[:,1])):
                for j in np.arange(0,len(shape[1,:]) - 1):
                    if shape[i,j]==0 and shape[i,j+1]!=0:
                        self.image[i,j]=255
                        self.active_outline.append((i,j))
                    if shape[i,j]==0 and shape[i,j-1]!=0:
                        self.image[i,j]=255
                        self.active_outline.append((i,j))
        for i in np.arange(0,len(shape[:,1]) - 1):
                for j in np.arange(0,len(shape[1,:])):
                    if shape[i,j]==0 and shape[i+1,j]!=0:
                        self.image[i,j]=255
                        self.active_outline.append((i,j))
                    if shape[i,j]==0 and shape[i-1,j]!=0:
                        self.image[i,j]=255
                        self.active_outline.append((i,j))
    
    def GetEnd(self, segment):
        if segment in ['TO', 'N', 'FH']:
            return 'na'
        else:
            return 'R'
    
    def EndlessCycle(self):
        while(1):
            result = cv2.addWeighted(self.image, 0.5, self.image, 1 - 0.5, 0)
            self.CreateWindow()
            
            cv2.setMouseCallback('Window',self.InteractiveDrawing)
            k=cv2.waitKey(1)&0xFF
            
            if k == ord("p"):
                cv2.imshow('Window',self.image)
            
            if k == ord("s"):
                self.DrawSegment()
            
            if k == ord("c"):
                self.CutSegment()
            
            if k==27:
                break


if __name__ == '__main__':
    png_file_path = r"C:\Users\Michal\kamera"
    text_files_path = r'C:\Users\Michal\kamera'
    missing_txt_files = []

    

    files = glob.glob(os.path.join(png_file_path,'*.png'))
    for file in files[0:1]:
        # im = Image.open(file)
        # im.show()
        image_test = cv2.imread(file)
        
        pripony1 = ['A','FA','H','N','S','T','TO']
        image_edit = ImageEdit(file, text_files_path)



