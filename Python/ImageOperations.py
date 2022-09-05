import numpy as np


def RotateImageLeft(original_array):
    rotated_array = np.asarray(list(reversed(list(zip(*original_array)))))
    return rotated_array

def RotateImageRight(original_array):
    rotated_array = np.asarray(list(zip(*original_array[::-1])))
    return rotated_array

def CreateOutline(image, shape):
    for i in np.arange(0,len(shape[:,1])):
            for j in np.arange(0,len(shape[1,:]) - 1):
                if shape[i,j]==0 and shape[i,j+1]!=0:
                    image[i,j]=255
                if shape[i,j]==0 and shape[i,j-1]!=0:
                    image[i,j]=255
    for i in np.arange(0,len(shape[:,1]) - 1):
            for j in np.arange(0,len(shape[1,:])):
                if shape[i,j]==0 and shape[i+1,j]!=0:
                    image[i,j]=255
                if shape[i,j]==0 and shape[i-1,j]!=0:
                    image[i,j]=255
    
    return image


if __name__ == "__main__":
    origo = np.array([[2,2,2],[3,3,3]])
    rotated_left = RotateImageLeft(origo)
    rotated_right = RotateImageRight(origo)
    