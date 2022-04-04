import easyocr
import cv2
import difflib
from .utils import IMAGE_PATH, IMAGE_RESIZED, IMAGE_GRAY
from .utils import get_best_match_score, get_best_match_username
from .utils import get_best_match_rank, sort_eascyocr_results


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
    _, im_bw = cv2.threshold(gray_image, 165, 255, cv2.THRESH_BINARY)
    pixel_width = im_bw.shape[0]
    cv2.imwrite('image-final.png', im_bw)

    reader = easyocr.Reader(['en'])
    results = reader.readtext(IMAGE_RESIZED)
    return sort_eascyocr_results(results, pixel_width)


def correct_easyOCR(line: list):
    """This calls the util functions to take
    the output provided by easyOCR and use that logic
    to correct common mistakes that are outputted.
    These include:
        - 21 instead of 2-1
        - 'username 2-1' instead of 'username,2-1'
        - correcting misspelt names using difflib."""

    if len(line) > 3:
        first = line.pop(0)
        last = line.pop()
        middle = "".join(line)
        line = [first, middle, last]
    if len(line) == 3:
        username = get_best_match_username(line[1])
        result = (f'{get_best_match_rank(line[0])},' +
                  f'{username[0][0]},,' +
                  f'{get_best_match_score(line[2])}')
        if username[1] == 'perfect':
            return result
        elif username[1] == 'pass':
            return f'{result},FIXED {line[1]} --> {username[0][0]}'
        elif username[1] == 'mixed':
            if difflib.SequenceMatcher(None, line[1], username[0][0]).ratio() == 1:
                return result
            else:
                o_options = ' vs '.join(username[0][0:])
                return f'{result},MIXED {o_options}'
        else:
            return f'{result},CHECK'
    return f'{",".join(line)},,,,CHECK'


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
        file.write(f"{correct_easyOCR(line)}\n")


def display_output(results: list):
    """This displays what easyocr found
    for quick proof reading for the user."""
    img = cv2.imread(IMAGE_RESIZED)
    for result in results:
        top_left = tuple([int(result[0][0][0]), int(result[0][0][1])])
        bottom_right = tuple([int(result[0][2][0]), int(result[0][2][1])])
        img = cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
    cv2.imwrite('image-displayed.png', img)
