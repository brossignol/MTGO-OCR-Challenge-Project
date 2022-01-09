import easyocr
import cv2
from .utils import IMAGE_PATH, IMAGE_RESIZED, IMAGE_GRAY, IMAGE_FINAL


async def run_easyocr() -> list:
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

    print("reading now")

    reader = easyocr.Reader(['en'])
    results = reader.readtext(IMAGE_FINAL)

    print("we done")

    return results
