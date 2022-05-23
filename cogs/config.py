import os
import easyocr

reader = easyocr.Reader(['en'])

IMAGE_PATH = 'image.png'
IMAGE_RESIZED = 'image-resized.png'
IMAGE_GRAY = 'image-gray.png'
IMAGE_FINAL = 'image-final.png'
IMAGE_DISPLAYED = 'image-displayed.png'

USERLIST = []
with open(os.path.join('usernames.txt')) as f:
    for line in f:
        username = line.strip()
        USERLIST.append(username)

SCORES = ['1-1-1', '2-1-1', '2-1-2', '2-1-3']
for i in range(0, 15):
    for j in range(0, 15):
        SCORES.append(f'{i}-{j}')
