import easyocr
import cv2
from .utils import IMAGE_PATH, IMAGE_RESIZED, IMAGE_GRAY, IMAGE_FINAL
from .utils import get_best_match_score, get_best_match_username


def run_easyocr() -> list:
    """This reads the uploaded image using
    easyocr and returns the easyocr generated
    list of tuples. It uses some preprocessing
    techniques that were tuned for mtgo images
    to improve accuracy."""

    # Resize Image
    img = cv2.imread(IMAGE_PATH, cv2.IMREAD_UNCHANGED)
    ratio = 2
    width = int(ratio * img.shape[1])
    height = int(ratio * img.shape[0])
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    cv2.imwrite(IMAGE_RESIZED, resized)

    # Grayscale Image
    img = cv2.cvtColor(cv2.imread(IMAGE_RESIZED), cv2.COLOR_BGR2RGB)  # fix color issue (rgb vs bgr)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(IMAGE_GRAY, gray_image)

    # Binary Image with Thresholding
    thresh, im_bw = cv2.threshold(gray_image, 165, 255, cv2.THRESH_BINARY)
    cv2.imwrite('image-final.png', im_bw)

    reader = easyocr.Reader(['en'])
    results = reader.readtext(IMAGE_FINAL)

    return results


def correct_easyOCR(line: list):
    """This fixes some common errors that easyOCR applies
    to mtgo data and returns it as a corrected csv string.\n
    These include:
        - 21 instead of 2-1
        - 'username 2-1' instead of 'username,2-1'
    This returs a string csv formatted to the challenge sheet setup."""

    corrected_list = []

    if len(line) == 2:
        corrected_list = line
    if len(line) > 2:
        corrected_list.append("".join(line[:-1]))
        corrected_list.append(line[-1])
    if len(corrected_list) == 2:
        username = get_best_match_username(corrected_list[0])
        if username[1] == 'pass':
            return f'{username[0]},,{get_best_match_score(corrected_list[1])}'
        else:
            return f'{username[0]},,{get_best_match_score(corrected_list[1])},CHECK'
    return f'{",".join(line)},,,CHECK'


def generate_csv(results: list):
    """generates a csv file from the results that
    easyOCR generated. This applies fine tuning to
    mtgo data images."""
    line = []
    level = 0  # used to add newline when word moves down a row
    with open("output.csv", "w") as file:
        for reading in results:
            if reading[0][0][0] < level:  # we are on a new line
                file.write(f"{correct_easyOCR(line)}\n")
                line = []
                line.append(reading[1])
            else:
                line.append(reading[1])
            level = reading[0][0][0]


def display_output(results: list):
    """This displays what easyocr found 
    for quick proof reading for the user."""
    img = cv2.imread(IMAGE_RESIZED)
    for result in results:
        top_left = tuple([int(result[0][0][0]), int(result[0][0][1])])
        bottom_right = tuple([int(result[0][2][0]), int(result[0][2][1])])
        img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),3)
    cv2.imwrite('image-displayed.png', img)
