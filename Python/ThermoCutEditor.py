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
import copy

class ImageEdit:
    def __init__(self, image_path, text_directory):
        self.text_directory = text_directory
        self.image_path = image_path
        self.drawing_enabled = False
        self.image_underlay = cv2.imread(image_path)
        self.image_overlay = np.zeros(self.image_underlay.shape, np.uint8)
        
        self.line_coordinates = []
        self.cut_line = []
        self.active_outline = []
        self.segment_names = []
        self.is_cut = False
        
        self.original_segments = dict()
        self.original_outlines = dict()
        self.active_segments = dict()
        self.active_outlines = dict()
        self.active_outline_points = dict()
        self.mask_names = dict()
        
        self.original_point = None
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
   
    def MouseEvents(self,event,x,y,flags,param):
        if event==cv2.EVENT_LBUTTONUP and self.is_cut == False and self.drawing_enabled == True:
            cv2.circle(self.image,(x,y),1,(0,0,255),-1)
            if self.line_coordinates !=[]:
                # cv2.line(self.image,(self.line_coordinates[-1][0],self.line_coordinates[-1][1]),
                #          (x,y),color = (0, 125, 0, 100), thickness = 5)
                
                rr, cc = line(self.line_coordinates[-1][1], self.line_coordinates[-1][0], y, x)
                self.image[rr, cc] = 1
                
                self.cut_line.append([rr,cc])
                
            self.line_coordinates.append([x,y])
            
        if event==cv2.EVENT_MBUTTONUP:
            x,y=self.line_coordinates[0][0],self.line_coordinates[0][1]
            cv2.circle(self.image,(x,y),1,(0,0,255),-1)
            if self.line_coordinates != []:
                cv2.line(self.image,(self.line_coordinates[-1][0],self.line_coordinates[-1][1]), (x,y),
                         color = (0, 125, 0), thickness = 1)
            self.line_coordinates.append([x,y])
    
    def CutSegment(self):
        self.DividePixels()
        
      
    def IfFolderNotExistCreateIt(self, path):
        isExist = os.path.exists(path)
        if not isExist:        
           os.makedirs(path)
        
    def SaveSubsegment(self):
        subsegment_array = np.zeros((640,480))
        for coords in self.subsegment_points:
            subsegment_array[coords[0], coords[1]] = 1
        
        subsegment_array_rotated = io.RotateImageLeft(subsegment_array)
        original_segment_rotated = io.RotateImageLeft(self.original_segments[self.active_segment_name])
        
        save_directory = os.path.join(self.text_directory, "originals")
        self.IfFolderNotExistCreateIt(save_directory)
        
        np.savetxt(os.path.join(save_directory, self.mask_names[self.active_segment_name]),
                   original_segment_rotated, fmt='%s', delimiter='\t', encoding = 'utf-8')
        
        new_segment_name = input("Give me a segment name: ")
        np.savetxt(os.path.join(self.text_directory, new_segment_name),
                   subsegment_array_rotated, fmt='%s', delimiter='\t', encoding = 'utf-8')
    
        print("done saving")
        
    def DrawAllSegments(self):
        for segment in ['A','FA','H','N','S','T','TO']:
            self.DrawSegment(segment)
        
    def DrawSegment(self, segment):
     
        side = self.GetEnd(segment)
        
        r = os.path.basename(self.image_path)
        s = os.path.splitext(r)[0]
        if s + '_' + segment + "_" + side + '.txt' in os.listdir(self.text_directory):
            self.mask_name = s + '_' + segment + "_" + side + '.txt'
            self.mask_names[segment] = self.mask_name
            self.original_segment = np.genfromtxt(os.path.join(self.text_directory,self.mask_name),delimiter='\t')
            self.segment_names.append(segment)
            
            mask_upright = io.RotateImageRight(self.original_segment)
            self.original_segments[segment] = mask_upright
            self.active_segments[segment] = mask_upright
            self.CreateOutline(mask_upright)
            self.MemorizeOriginalOutline(segment)
           
            self.image = cv2.addWeighted(self.image_underlay,0.9,self.image_overlay,0.4,0)
            cv2.imshow('Window',self.image)
    
    def CreateOutline(self, shape):
        self.filtered_coordinates = io.CreateOutlineCV(self.image_overlay, shape)
        print('a',len(self.filtered_coordinates))
    
    def MemorizeOriginalOutline(self, segment):
        self.original_outlines[segment] = self.filtered_coordinates
        self.active_outlines[segment] = self.filtered_coordinates
     
    def RedrawOutlines(self, outline_names):
        self.image_overlay = np.zeros(self.image_underlay.shape, np.uint8)
        for segment in outline_names:
            io.ColorTheOutline(self.image_overlay,self.active_outlines[segment])
        
        self.image = cv2.addWeighted(self.image_underlay,0.9,self.image_overlay,0.4,0)
        cv2.imshow('Window',self.image)
        print("redrawn")
    
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
      
    def CutIn(self):
        self.Cut()
        
        try:
            self.subsegment_points = copy.deepcopy(self.active_segment_points)
            self.subsegment_array = copy.deepcopy(self.original_segments[self.active_segment_name])
            
            for x,y in zip(self.values[0], self.values[1]):
                is_already_in_segment = False
                for segment_point in self.active_segment_points:
                    if x == segment_point[0] and y == segment_point[1]:
                        is_already_in_segment = True
                    
                if is_already_in_segment == False:
                    self.subsegment_points.append([x,y])
                    self.subsegment_array[x,y] = 1
           
            self.MemorizeNewSegment(self.subsegment_array, io.CreateOutlineCV(self.image_overlay,self.subsegment_array))
            self.RedrawOutlines([self.active_segment_name])
            self.EndOperation()
        except Exception as e:
            print(e)
            print("probably no segment selected")
        
    def CutOut(self):      
        self.Cut()
        self.subsegment_points = []
        self.subsegment_array = np.zeros((640,480))
                
        try:
            for segment_point in self.active_segment_points:
                is_already_in_segment = False
                for x,y in zip(self.values[0], self.values[1]):
                    if x == segment_point[0] and y == segment_point[1]:
                        is_already_in_segment = True
                
                if is_already_in_segment == False:
                    self.subsegment_points.append(segment_point)
                    print(segment_point[0], segment_point[1])
                    self.subsegment_array[segment_point[0], segment_point[1]] = 1
            
            self.MemorizeNewSegment(self.subsegment_array, io.CreateOutlineCV(self.image_overlay,self.subsegment_array))
            self.RedrawOutlines([self.active_segment_name])
            self.EndOperation()
        
        except Exception as e:
            print(e)
            print("probably no segment selected")
    
    def MemorizeNewSegment(self, map_array, outline_coordinates):
        self.active_segments[self.active_segment_name] = map_array
        self.active_outlines[self.active_segment_name] = outline_coordinates
    
    def Cut(self):
        mask = np.zeros((self.image.shape), dtype=np.uint8)
        points = np.array([self.line_coordinates], dtype=np.int32)
        cv2.fillPoly(mask, points, (255,255,255))
        self.values = np.where((mask == (255,255,255)).all(axis=2))
    
    def EndOperation(self):
        print("operation ended")
        self.EnablePanning()
        self.line_coordinates = []
    
    def ActivateSegment(self, segment):
        self.active_segment_points = io.GetCoordinatesOfSegment(self.active_segments[segment])
        self.active_segment_name = segment
        self.RedrawOutlines([self.active_segment_name])
    
    def IsDrawingEnabled(self):
        return self.drawing_enabled
    
    def EnableDrawing(self):
        self.drawing_enabled = True
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_CROSS))
        
    def EnablePanning(self):
        self.drawing_enabled = False
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
    
    def RedrawAllSegments(self):
        self.RedrawOutlines(self.segment_names)
    
    def EndlessCycle(self):
        self.DrawAllSegments()
        cv2.setMouseCallback('Window',self.MouseEvents)
        while(1):
            result = cv2.addWeighted(self.image, 0.5, self.image, 1 - 0.5, 0)
            self.CreateWindow()
            
            
            key=cv2.waitKey(1)&0xFF
            last_key = key
            
            if key == ord("p"):
                cv2.imshow('Window',self.image)
            
            if key == ord('u'):
                if self.IsDrawingEnabled() == False:
                    self.EnableDrawing()
                else:
                    self.EnablePanning()
            
            if key == ord('w'):
                self.SaveSubsegment()
           
            if key == ord("s"):
                self.ActivateSegment('S')
            if key == ord("a"):
                self.ActivateSegment('A')
            if key == ord("f"):
                self.ActivateSegment('FA')
            if key == ord("t"):
                self.ActivateSegment('T')
            if key == ord("h"):
                self.ActivateSegment('H')
            if key == ord("n"):
                self.ActivateSegment('N')
            if key == ord("r"):
                self.ActivateSegment('TO')
            
            if key == ord("o"):
                self.RedrawAllSegments()
            
            if key == ord('z'):
                self.CutIn()
            
            if key == ord('m'):
                self.CutOut()
            
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
    png_file_path = r"F:\Ph.D\camera_processing\30"
    text_files_path = r'F:\Ph.D\camera_processing\30'
    missing_txt_files = []

    files = glob.glob(os.path.join(png_file_path,'*.png'))
    for file in files[0:1]:
        # im = Image.open(file)
        # im.show()
        image_test = cv2.imread(file)
        
        pripony1 = ['A','FA','H','N','S','T','TO']
        image_edit = ImageEdit(file, text_files_path)



