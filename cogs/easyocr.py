import easyocr
import cv2
from .utils import score_readings, correct_scores, IMAGE_PATH, IMAGE_DOUBLE, IMAGE_FINAL


def read_image(mtgo_data=False) -> list:
    """This reads the image that was saved. Uses some
    preprocessing and post processing for mtgo data
    images. Standard easyOCR for anything else."""
    reader = easyocr.Reader(['en'])

    if mtgo_data:
        print("double mtgo image")
        img = cv2.imread(IMAGE_PATH, cv2.IMREAD_UNCHANGED)
        width = int(2 * img.shape[1])
        height = int(2 * img.shape[0])
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        cv2.imwrite('image-double.png', resized)
        
        print("grey thresh mtgo image")
        img = cv2.cvtColor(cv2.imread(IMAGE_DOUBLE), cv2.COLOR_BGR2RGB) # fix color issue (rgb vs bgr)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh, im_bw = cv2.threshold(gray_image, 175, 130, cv2.THRESH_BINARY)
        cv2.imwrite('image-final.png', im_bw)
        
        print("now reading mtgo image")
        result = reader.readtext(IMAGE_FINAL)
    else:
        print("reading regular image")
        result = reader.readtext(IMAGE_PATH)

    generate_csv(result, mtgo_data)
    display_easyOCR(result, mtgo_data)


def display_easyOCR(result: list, mtgo_data: bool):
    """This displays an image of what easyocr was able to spot in the image"""
    print("generating display")
    if mtgo_data:
        img = cv2.imread(IMAGE_DOUBLE)
    else:
        img = cv2.imread(IMAGE_PATH)
    for reading in result:
        top_left = tuple([int(reading[0][0][0]), int(reading[0][0][1])])
        bottom_right = tuple([int(reading[0][2][0]), int(reading[0][2][1])])
        img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),3)
    cv2.imwrite('image-displayed.png', img)

def generate_csv(result: list, mtgo_data: bool):
    """generates a csv file from the results that
    easyOCR generated. This applies fine tuning to
    mtgo data images. For anything else, it returns
    what easyOCR found."""
    
    print("generating csv")

    if mtgo_data:
        level = 0 # used to add newline when word moves down a row
        with open("output.csv", "w") as file:
            for reading in result:
                if reading[0][0][0] < level: # we are on a new line
                    level = reading[0][0][0]
                    file.write(f"\n{correct_easyOCR(reading[1], True)},")
                else:
                    level = reading[0][0][0]
                    file.write(f"{correct_easyOCR(reading[1], True)},")
    else:
        with open("output.csv", "w") as file:
            for reading in result:
                file.write(f"{reading[1]},\n")


def correct_easyOCR(reading: str, newline: bool):
    """This fixes some common errors that easyOCR applies
    to mtgo data and returns it as a corrected csv string.\n
    These include:
        - 21 instead of 2-1
        - 'username 2-1' instead of 'username,2-1'"""
    
    r = reading.split()
    bad_string = False
    
    if len(r) > 1:
        for element in r:
            if element in score_readings:
                bad_string = True    
    if not newline:
        for i in range(len(r)):
            if r[i] in correct_scores.keys():
                r[i] = correct_scores[r[i]]
    if bad_string:
        return ','.join(r)
    else:
        return ''.join(r)
