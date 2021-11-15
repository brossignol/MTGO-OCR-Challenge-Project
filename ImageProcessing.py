#!/usr/bin/env python
# coding: utf-8

# In[1]:


import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np


# In[2]:


IMAGE_PATH2 = 'data2.png'
IMAGE_PATH = 'data.png'
IMAGE_PATH_GRAY = 'data-gray.png'
IMAGE_PATH_GRAY_THRESH = 'data-gray-thresh.png'
IMAGE_PATH_DILATED = 'data-dilated.png'
IMAGE_PATH_ERODED = 'data-eroded.png'


# In[4]:


# save stock gray image
img = cv2.cvtColor(cv2.imread(IMAGE_PATH), cv2.COLOR_BGR2RGB) # fix color issue (rgb vs bgr)
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite("data-gray.png", gray_image)


# In[5]:


# save the best black white thresholded image 
# currently I believe it is (170, 130)
thresh, im_bw = cv2.threshold(gray_image, 145, 130, cv2.THRESH_BINARY)
cv2.imwrite("data-gray-thresh.png", im_bw)


# In[6]:


# dilate the font from the BW image to improve accuracy
def thick_font(image):
    image = cv2.bitwise_not(image)
    kernel = np.ones((1,2),np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return (image)
dilated_image = thick_font(im_bw)
cv2.imwrite("data-dilated.png", dilated_image)


# In[7]:


# dilate the font from the BW image to improve accuracy
def erode_font(image):
    kernel = np.ones((3,1),np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    return (image)
eroded_image = erode_font(im_bw)
cv2.imwrite("data-eroded.png", eroded_image)


# In[ ]:


# read in pre-processed image using easy ocr
reader = easyocr.Reader(['en'], gpu=False)
result = reader.readtext(IMAGE_PATH_GRAY)


# In[149]:


# this displays an image of what easyocr was able to spot in the image.
# NOTE: the image shown is the original image, not the image that was preprocessed
# and given to easyocr.
img = cv2.imread(IMAGE_PATH)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # fix color issue (rgb vs bgr)
for reading in result:
    top_left = tuple([int(reading[0][0][0]), int(reading[0][0][1])])
    bottom_right = tuple([int(reading[0][2][0]), int(reading[0][2][1])])
    img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),3)
print(len(result)) # higher the number, better the accuracy
plt.figure(figsize=(50, 20))
plt.imshow(img)


# In[151]:


for reading in result:
    print(reading)


# In[64]:


img = cv2.imread(IMAGE_PATH)
reading = result[-1]
    top_left = tuple(int(reading[0][0]))
    bottom_right = tuple(int(reading[0][2]))
    img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),3)
plt.figure(figsize=(50, 20))
plt.imshow(img)


# In[82]:


# HELPER FUNCTION STUFF TO FIND OPTIMAL THRESHOLD FOR BW IMAGE

# this uses image preprocessing to try and get an image 
# better fit for the easyocr model.

def display(im_path):
    # code I ripped off stackoverflow to display images nicely. (https://stackoverflow.com/questions/28816046/)
    dpi = 80
    im_data = plt.imread(im_path)

    height, width  = im_data.shape[:2]
    
    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    ax.axis('off')

    # Display the image.
    ax.imshow(im_data, cmap='gray')

    plt.show()

img = cv2.cvtColor(cv2.imread(IMAGE_PATH), cv2.COLOR_BGR2RGB) # fix color issue (rgb vs bgr)

# loop through all possible grayscale combo's and look for the best one. (170, 130) for now.
for i in range(10, 250, 10):
    for j in range(10, 250, 10):
        print(i, j)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh, im_bw = cv2.threshold(gray_image, i, j, cv2.THRESH_BINARY)
        cv2.imwrite("data-gray-thresh.png", im_bw)
        display("data-gray-thresh.png")

