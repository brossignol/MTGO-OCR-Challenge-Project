import os

IMAGE_PATH = 'image.png'
IMAGE_DOUBLE = 'image-double.png'
IMAGE_FINAL = 'image-final.png'
IMAGE_DISPLAYED = 'image-displayed.png'

# Stores possible score readings that easyOCR might generate. 
score_readings = []
for i in range (0, 15):
    for j in range (0, 15):
        score_readings.append(f'{i}{j}')
        score_readings.append(f'{i}-{j}')
    score_readings.append(f'{i}')

# A dictionary to map bad score readings from easyOCR,
# to good their correct counterpart. example: xy --> x-y
correct_scores = {}
for i in range (0, 15):
    for j in range (0, 15):
        correct_scores[f'{i}{j}'] = f'{i}-{j}'

def cleanup(mtgo):
    """removes image from system after reading."""
    if mtgo:
        os.remove('image-double.png')
        os.remove('image-final.png')
    os.remove('image.png')
    os.remove('output.csv')

