import numpy as np
import cv2
from skimage.draw import line

def RotateImageLeft(original_array):
    rotated_array = np.asarray(list(reversed(list(zip(*original_array)))))
    return rotated_array

def RotateImageRight(original_array):
    rotated_array = np.asarray(list(zip(*original_array[::-1])))
    return rotated_array

def CreateOutlineCV(image, shape):
    
    outline_coordinates = []
    for i in np.arange(0,len(shape[:,1])):
            for j in np.arange(0,len(shape[1,:]) - 1):
                if shape[i,j]==0 and shape[i,j+1]!=0:
                    outline_coordinates.append((i,j))
                if shape[i,j]==0 and shape[i,j-1]!=0:
                    outline_coordinates.append((i,j))
    for i in np.arange(0,len(shape[:,1]) - 1):
            for j in np.arange(0,len(shape[1,:])):
                if shape[i,j]==0 and shape[i+1,j]!=0:
                    outline_coordinates.append((i,j))
                if shape[i,j]==0 and shape[i-1,j]!=0:
                    outline_coordinates.append((i,j))
    
    filtered_coordinates = ColorTheOutline(image,outline_coordinates)
    return filtered_coordinates

def ColorTheOutline(image, outline_coordinates):
    color = [0,34,252]
    filtered_coordinates = []
    for point_coordinate in np.arange(1, len(outline_coordinates),1):
        
        rr, cc = line(outline_coordinates[point_coordinate-1][1],outline_coordinates[point_coordinate-1][0],
                      outline_coordinates[point_coordinate][1], outline_coordinates[point_coordinate][0])
        PaintPixel(image, (rr[0],cc[0]), (0,0,255))
        filtered_coordinates.append([cc[0],rr[0]])
        
    return filtered_coordinates 

def PaintPixel(image, coordinates, color):
    image[coordinates[1], coordinates[0]]=color
    
def CreateOutlinePil(image, shape):
    for i in np.arange(0,len(shape[:,1])):
        for j in np.arange(0,len(shape[1,:]) - 1):
            if shape[i,j]==0 and shape[i,j+1]!=0:
                ColorPixel(image, (j,i), (227, 2, 2, 200))
                # image.putpixel((i,j), (230, 209, 23, 255))
            if shape[i,j]==0 and shape[i,j-1]!=0:
                ColorPixel(image, (j,i), (227, 2, 2, 200))
                # pixels[i,j]=(230, 209, 23, 255)
    for i in np.arange(0,len(shape[:,1]) - 1):
        for j in np.arange(0,len(shape[1,:])):
            if shape[i,j]==0 and shape[i+1,j]!=0:
                ColorPixel(image, (j,i), (227, 2, 2, 200))
            if shape[i,j]==0 and shape[i-1,j]!=0:
                ColorPixel(image, (j,i), (227, 2, 2, 200))
    
    return image

def ColorPixel(image, coordinates, color):
    image.putpixel(coordinates, color)
    
def GetCoordinatesOfSegment(segment_array):
    coordinate_array = []
    for i in np.arange(0,len(segment_array[:,1])):
        for j in np.arange(0,len(segment_array[1,:]) - 1):
            if segment_array[i,j]!=0:
                coordinate_array.append([i,j])
    
    return coordinate_array
    

if __name__ == "__main__":
    origo = np.array([[2,2,2],[3,3,3]])
    rotated_left = RotateImageLeft(origo)
    rotated_right = RotateImageRight(origo)
    