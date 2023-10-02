import easyocr
import cv2
import asyncio
import difflib
from .config import IMAGE_PATH, IMAGE_RESIZED, IMAGE_GRAY
from .utils import get_best_match_score, get_best_match_username


def run_easyocr(image_path=IMAGE_PATH) -> list:
    """This reads the uploaded image using
    easyocr and returns the easyocr generated
    list of tuples. It uses some preprocessing
    techniques that were tuned for mtgo images
    to improve accuracy."""

    # Resize Image
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
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
    results = reader.readtext(IMAGE_RESIZED)
    return sort_eacyocr(results, im_bw)


async def run_async_easyocr() -> list:
    """This creates a seperate thread for this function
    to run on to prevent blocking in discord."""
    return await asyncio.to_thread(run_easyocr)


def sort_eacyocr(results: list, im_bw: object) -> list:
    """This function helps handle the corner case where easyOCR
    bugs out. This bug occurs when a row has decimal values for the
    location list in the tuple. When this occur, that row is misplaced
    at the bottom of the outputted list, resulting in an incorrect order.
    This fixes that by running a sort algorithm on the output.

        example of bug:
            bugged output - [1, 2, 3, 4, 2.3]
            corrected output - [1, 2, 2.3, 3, 4]"""

    # standardize the list of y-values so they can be used as row numbers
    # pproteus wrote this
    pixel_width = im_bw.shape[0]
    CELL_WIDTH_MULTIPLIER = 1/75
    CELL_HEIGHT_MULTIPLIER = 1/200
    points = [i[0][0] for i in results]
    rows = []
    columns = []
    for point in points:
        for row in rows:
            # if this box is close to other boxes, add it to that bin
            if abs(sum(row) / len(row) - point[1]) < (pixel_width*CELL_HEIGHT_MULTIPLIER):
                row += point[1],
                break
        # if it's not close to anybody so far, make a new bin
        else:
            rows += [point[1]],

        for column in columns:
            # if this box is close to other boxes, add it to that bin
            if abs(sum(column) / len(column) - point[0]) < (pixel_width*CELL_WIDTH_MULTIPLIER):
                column += point[0],
                break
        # if it's not close to anybody so far, make a new bin
        else:
            columns += [point[0]],

    # get a single number to represent each bin
    rows = sorted([round(sum(i) / len(i)) for i in rows])
    columns = sorted([round(sum(i) / len(i)) for i in columns])

    # overwrite the top and left lines of the bounding boxes
    for result in results:
        result[0][0][1] = result[0][1][1] = min(rows, key=lambda x: abs(x - result[0][0][1]))
        result[0][0][0] = result[0][3][0] = min(columns, key=lambda x: abs(x - result[0][0][0]))

    results.sort(key=lambda x: x[0][0][::-1])
    return results


def correct_easyOCR(line: list) -> str:
    """This corrects common easyOCR errors and returns
    it in the corrected csv format.

    corrected errors:
        - 'user,name,2-1' instead of 'username,2-1'
        - incorrectly formatted results (21 vs 2-1)
        - incorrect usernames

    csv format:
        username|archetype|record|comments

    Archetype is left blank as this is not present in
    the screenshot.

    example output
        - username,,9,1,FIXED usernam -->username"""

    corrected_list = []

    if len(line) == 2:
        corrected_list = line
    if len(line) > 2:
        corrected_list.append("".join(line[:-1]))
        corrected_list.append(line[-1])
    if len(corrected_list) == 2:
        username = get_best_match_username(corrected_list[0])
        if username[1] == 'perfect':
            comment = ''
        elif username[1] == 'fixed':
            comment = f'FIXED {corrected_list[0]} --> {username[0][0]}'
        elif username[1] == 'mixed':
            if difflib.SequenceMatcher(None, corrected_list[0], username[0][0]).ratio() == 1:
                comment = ''
            else:
                mixed = ' vs '.join(username[0][0:])
                comment = f'MIXED {mixed}'
        else:
            comment = 'CHECK'
        username = username[0][0]
        archetype = ''
        record = get_best_match_score(corrected_list[1])
        return f'{username},{archetype},{record},{comment}'
    else:
        # ocr screwed up big time
        return f'{",".join(line)},,,CHECK'


def generate_csv(results: list) -> None:
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


def display_output(results: list) -> None:
    """This displays what easyocr found
    for quick proof reading for the user."""
    img = cv2.imread(IMAGE_RESIZED)
    for result in results:
        top_left = tuple([int(result[0][0][0]), int(result[0][0][1])])
        bottom_right = tuple([int(result[0][2][0]), int(result[0][2][1])])
        img = cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
    cv2.imwrite('image-displayed.png', img)
