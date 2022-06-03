import cv2
import numpy as np
import easyocr

from cogs.config import IMAGE_PATH
from cogs.utils import get_best_match_score, get_best_match_username


def split_long_box(coord, name, score):
    """
    Split long box at each space.
    """
    x1, x2, y1, y2 = coord[0][0], coord[2][0], coord[0][1], coord[2][1]

    cum = 0
    for s in name.split(' '):
        if len(s) == 0:
            cum += 1
            continue
        l = len(s)
        xa = cum / len(name) * (x2 - x1) + x1
        xb = (cum + l) / len(name) * (x2 - x1) + x1
        cum += l + 1

        coord = [[xa, y1], [xb, y1], [xb, y2], [xa, y2]]

        yield coord, s, score


def format_results(results):
    """
    Split long box at each space.
    """
    res = []
    for coord, name, score in results:
        if ' ' in name:
            res.extend(split_long_box(coord, name, score))
        else:
            res.append((coord, name, score))
    return res


def compute_grid(res, img_shape):
    """
    Find rows and columns positions from boxes positions.
    """
    xs = np.zeros(img_shape[1])
    ys = np.zeros(img_shape[0])
    for r in res:
        coord, name, score = r
        (x1, y1), _, (x2, y2), _ = coord

        xs[int(x1): int(x2)] = 1
        ys[int(y1): int(y2)] = 1

    idx = np.where(xs)[0]
    cols = idx[np.where(np.diff(idx) > 1)[0] + 1]

    idx = np.where(ys)[0]
    rows = idx[np.where(np.diff(idx) > 1)[0] + 1]

    return cols, rows


def place_box_in_grid(res, cols, rows):
    """
    Find box placement on grid
    """
    grid = [[[] for _ in range(len(rows) + 1)] for _ in range(len(cols) + 1)]

    for r in res:
        coord, name, score = r
        (x1, y1) = coord[0]

        i = np.searchsorted(cols, int(x1), side='right')
        j = np.searchsorted(rows, int(y1), side='right')

        grid[i][j].append((x1, name))

    df = []
    for col in grid:
        df.append([])
        for row in col:
            s = [a[1] for a in sorted(row)]
            df[-1].append('_'.join(s))

    # df = list(zip(*df))
    return df


def display_result(img, res, cols, rows):
    """
    Display boxes, columns and rows on image.
    """
    img_ = img.copy()
    for result in res:
        top_left = tuple([int(result[0][0][0]), int(result[0][0][1])])
        bottom_right = tuple([int(result[0][2][0]), int(result[0][2][1])])
        img_ = cv2.rectangle(img_, top_left, bottom_right, (0, 255, 0), 3)

    for col in cols:
        img_ = cv2.line(img_, (col, 0), (col, img.shape[0]), color=(0, 0, 255), thickness=3)
    for row in rows:
        img_ = cv2.line(img_, (0, row), (img.shape[1], row), color=(0, 0, 255), thickness=3)

    return img_


def column_type(col):
    """
    Assert columns type to lead autocorrection.
    """
    s = ''.join(col)
    if len(s) == 0:
        return ''

    n_digits = sum(map(str.isdigit, s))
    if n_digits < 0.3 * len(s):
        return 'Name'

    n_dash = s.count('-')

    n_c = sum([c in {'0', '1', '2', '-'} for c in s])

    if n_dash > 0.1 * len(s) or n_c >= 0.9 * len(s):
        return 'Score'

    return 'Rank'


def get_best_match_score_2(score):
    s = get_best_match_score(score.replace('Z', '2')).replace(',', '-')
    if len(s) == 1:
        return s + '-0'  # seems to be a common mistake
    else:
        return s


def correct_detection(df):
    """
    Correct ocr detection depending on column type.
    """
    df_ = []
    for col in df:
        t = column_type(col)
        if t == 'Name':
            df_.append([get_best_match_username(name)[0][0] for name in col])
        elif t == 'Score':
            df_.append([get_best_match_score_2(score) for score in col])
        else:
            df_.append(col)
    return df_


def process_results(results, img_shape):
    """
    Return processed result and display argument.
    """
    res = format_results(results)
    cols, rows = compute_grid(res, img_shape)
    df = place_box_in_grid(res, cols, rows)
    df = correct_detection(df)

    return df, (res, cols, rows)


def generate_csv_grid(path, df):
    with open(path, 'w') as file:
        for row in zip(*df):
            file.write(','.join(row) + '\n')


def load_image():
    """
    Load image and apply pre-treatment.
    """
    img = cv2.imread(IMAGE_PATH, cv2.IMREAD_UNCHANGED)
    ratio = 2
    width = int(ratio * img.shape[1])
    height = int(ratio * img.shape[0])
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh, im_bw = cv2.threshold(gray_image, 165, 255, cv2.THRESH_BINARY)
    return img, im_bw


def run_easyocr_multi():
    img, im_bw = load_image()

    reader = easyocr.Reader(['en'])
    results = reader.readtext(im_bw)

    df, args = process_results(results, img.shape)
    generate_csv_grid("output.csv", df)

    img_res = display_result(img, *args)
    cv2.imwrite('image-displayed.png', img_res)
