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
import win32api
import win32con

class ImageEdit:
    def __init__(self, image_path, text_directory):
        self.text_directory = text_directory
        self.image_path = image_path
        self.mode = True
        self.image = cv2.imread(image_path)
        self.line_coordinates = []
        self.cut_line = []
        self.active_outline = []
        self.is_cut = False
        self.subsegment_a = np.zeros((640,480))
        self.subsegment_b = np.zeros((640,480))
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
        crossing_points = self.FindCrossings()
        x1 = min([i[1] for i in crossing_points])
        x2 = max([i[1] for i in crossing_points])
        y1 = crossing_points[np.argmin([i[1] for i in crossing_points])][0]
        y2 = crossing_points[np.argmax([i[1] for i in crossing_points])][0]
       
        self.line_x = []
        self.line_y = []
       
        fit = np.polyfit(self.cut_line[0][1], self.cut_line[0][0], 1)
        fit2 = np.polyfit(self.cut_line[0][0], self.cut_line[0][1], 1)
        if y1 < y2:
        
            for i in self.shape_coordinates:
                y_coord = i[0]
                x_coord = i[1]
                
                x_line = self.ExtrapolateForGivenY(fit2, y_coord)
                y_line = self.ExtrapolateForGivenX(fit, x_coord)
                                
                self.line_x.append(int(y_line))
                self.line_y.append(int(x_line))
                if y_coord < y_line or x_coord > x_line:
                    self.subsegment_a[y_coord, x_coord] = 1
                else:
                    self.subsegment_b[y_coord, x_coord] = 1
        
        elif y1 >= y2:
            for i in self.shape_coordinates:
                y_coord = i[0]
                x_coord = i[1]
                
                x_line = self.ExtrapolateForGivenY(fit2, y_coord)
                y_line = self.ExtrapolateForGivenX(fit, x_coord)
                                
                self.line_x.append(int(y_line))
                self.line_y.append(int(x_line))
                if y_coord < y_line or x_coord < x_line:
                    self.subsegment_a[y_coord, x_coord] = 1
                else:
                    self.subsegment_b[y_coord, x_coord] = 1 
                
        self.CreateOutline(self.subsegment_a, 0)
        self.CreateOutline(self.subsegment_b, 125)
        print("done")
        self.is_cut = True
        # cv2.setMouseCallback('Window',self.HoverOverSubsegment)
        cv2.imshow('Window',self.image)
        
    
    def ExtrapolateForGivenY(self, fit, given_y):
        line = np.poly1d(fit)
        new_point = line(given_y)
        return new_point
    
    def ExtrapolateForGivenX(self, fit, given_x):        
        line = np.poly1d(fit)
        new_point = line(given_x)
        return new_point
    
    def MouseEvents(self,event,x,y,flags,param):
        global ix,iy,drawing, mode
        if event==cv2.EVENT_LBUTTONDOWN:
            drawing=True
        
        if event==cv2.EVENT_LBUTTONUP and self.is_cut == False:
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
            
            
        if event == cv2.EVENT_LBUTTONUP and self.is_cut == True:
            if self.subsegment_a[y,x] != 0:
                print("sega")
                data_to_write = io.RotateImageLeft(self.subsegment_a)
                
                # file_name = input("name of the file")
                # np.savetxt(os.path.join(r"C:\Users\Michal\kamera", self.mask_name),
                #            self.data_to_write, fmt='%s', delimiter='\t', encoding = 'utf-8')
                
                self.SaveSubsegment(data_to_write)
                
            if self.subsegment_b[y,x] != 0:
                print("segb")
                data_to_write = io.RotateImageLeft(self.subsegment_b)
                self.SaveSubsegment(data_to_write)
                
        if event == cv2.EVENT_MOUSEMOVE:
           
            if self.subsegment_a[y,x] != 0 or self.subsegment_b[y,x] != 0:
                win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
                
            else:
                win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_ARROW))
        
    def CutSegment(self):
        self.DividePixels()
         
    def SaveSubsegment(self, data_to_save):
        np.savetxt(os.path.join(r"C:\Users\Michal\kamera", self.mask_name),
                   data_to_save, fmt='%s', delimiter='\t', encoding = 'utf-8')
    
    def DrawAllSegments(self):
        for segment in ['A','FA','H','N','S','T','TO']:
            self.DrawSegment(segment)
        
    def DrawSegment(self, segment):
        # pripony1 = ['A','FA','H','N','S','T','TO']
        # for segment in pripony1:
        side = self.GetEnd(segment)
        
        r = os.path.basename(self.image_path)
        s = os.path.splitext(r)[0]
        if s + '_' + segment + "_" + side + '.txt' in os.listdir(self.text_directory):
            self.mask_name = s + '_' + segment + "_" + side + '.txt'
            mask = np.genfromtxt(os.path.join(self.text_directory,self.mask_name),delimiter='\t')
            mask_upright = io.RotateImageRight(mask)
            self.CreateOutline(mask_upright)
            # cv2.circle(mask,(240,320),280,1,thickness=-1)
            
            # res = cv2.bitwise_not(self.image,self.image,mask = np.int8(mask_outer))
            cv2.imshow('Window',self.image)
    
    def CreateOutline(self, shape):
        io.CreateOutlineCV(self.image, shape)
       
    def GetEnd(self, segment):
        if segment in ['TO', 'N', 'FH']:
            return 'na'
        else:
            return 'R'
    
    def Restart(self):
        cv2.destroyAllWindows()
        self.image = cv2.imread(self.image_path)
        self.CreateWindow()
        self.DrawAllSegments()
        self.is_cut = False
        cv2.setMouseCallback('Window',self.MouseEvents)
        self.cut_line = []
        self.line_coordinates = []
        self.subsegment_a = np.zeros((640,480))
        self.subsegment_b = np.zeros((640,480))
        
    
    def EndlessCycle(self):
        self.DrawAllSegments()
        while(1):
            result = cv2.addWeighted(self.image, 0.5, self.image, 1 - 0.5, 0)
            self.CreateWindow()
            
            cv2.setMouseCallback('Window',self.MouseEvents)
            key=cv2.waitKey(1)&0xFF
            last_key = key
            
            if key == ord("p"):
                cv2.imshow('Window',self.image)
            
            if key == ord("s"):
                self.DrawSegment("S")
            if key == ord("a"):
                self.DrawSegment("A")
            if key == ord("f"):
                self.DrawSegment("FA")
            if key == ord("t"):
                self.DrawSegment("T")
            if key == ord("h"):
                self.DrawSegment("H")
            if key == ord("n"):
                self.DrawSegment("N")
            if key == ord("r"):
                self.DrawSegment("TO")
            
            if key == ord("c"):
                self.CutSegment()
            
            if key == ord("o"):
                self.Restart()
            
            if key==27:
                break


class Segment:
    def CreateFromTxt(self, txt_file_path):
        self.segment_mask = np.genfromtxt(txt_file_path,delimiter='\t')

    def SaveIntoTxt(self, txt_file_path):
        np.savetxt(txt_file_path, self.segment_mask)

    def CreateFromArray(self, array):
        self.segment_mask =  array                  

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



