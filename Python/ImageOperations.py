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
    
    # for i in np.arange(0,len(shape[:,1])):
    #         for j in np.arange(0,len(shape[1,:]) - 1):
    #             if shape[i,j]==0 and shape[i,j+1]!=0:
    #                 image[i,j]=color
    #             if shape[i,j]==0 and shape[i,j-1]!=0:
    #                 image[i,j]=color
    # for i in np.arange(0,len(shape[:,1]) - 1):
    #         for j in np.arange(0,len(shape[1,:])):
    #             if shape[i,j]==0 and shape[i+1,j]!=0:
    #                 image[i,j]=color
    #             if shape[i,j]==0 and shape[i-1,j]!=0:
    #                 image[i,j]=color
    
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
    
    ColorTheOutline(image,outline_coordinates)
    return image

def ColorTheOutline(image, outline_coordinates):
    color = [0,34,252]
    for point_coordinate in np.arange(1, len(outline_coordinates),5):
        # cv2.line(image,(outline_coordinates[point_coordinate-1][0],outline_coordinates[point_coordinate-1][1]),
        #           (outline_coordinates[point_coordinate][0],outline_coordinates[point_coordinate][1]),
        #           color = (0, 125, 0, 100), thickness = 1)
        rr, cc = line(outline_coordinates[point_coordinate-1][1],outline_coordinates[point_coordinate-1][0],
                      outline_coordinates[point_coordinate][1], outline_coordinates[point_coordinate][0])
        cv2.circle(image,(rr[0],cc[0]),1,(0,0,255),-1)
        # image[rr, cc] = 1
        
        
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
    

if __name__ == "__main__":
    origo = np.array([[2,2,2],[3,3,3]])
    rotated_left = RotateImageLeft(origo)
    rotated_right = RotateImageRight(origo)
    