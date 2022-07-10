import cv2
import numpy as np
import easyocr

from cogs.config import IMAGE_PATH
from cogs.utils import get_best_match_score, get_best_match_username, get_best_match_score_multi


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


def compute_grid(res, img_shape, buffer=1):
    """
    Find rows and columns positions from boxes positions.
    """
    xs = np.zeros(img_shape[1])
    ys = np.zeros(img_shape[0])
    for r in res:
        coord, name, score = r
        (x1, y1), _, (x2, y2), _ = coord

        xs[int(x1) + buffer: int(x2) - buffer] = 1
        ys[int(y1) + buffer: int(y2) - buffer] = 1

    idx = np.where(xs)[0]
    cols = idx[np.where(np.diff(idx) > 1)[0] + 1] - buffer

    idx = np.where(ys)[0]
    rows = idx[np.where(np.diff(idx) > 1)[0] + 1] - buffer

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

    return df


def display_result(img, res, cols, rows):
    """
    Display boxes, columns and rows on image.
    """
    img_ = img.copy()
    for result in res:
        top_left = tuple([int(result[0][0][0]), int(result[0][0][1])])
        bottom_right = tuple([int(result[0][2][0]), int(result[0][2][1])])
        img_ = cv2.rectangle(img_, top_left, bottom_right, (0, 255, 0, 255), 3)

    for col in cols:
        img_ = cv2.line(img_, (col, 0), (col, img.shape[0]), color=(255, 0, 0, 255), thickness=3)
    for row in rows:
        img_ = cv2.line(img_, (0, row), (img.shape[1], row), color=(255, 0, 0, 255), thickness=3)

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

    if n_c >= 0.7 * len(s):
        return 'Score'

    if n_dash > 0.1 * len(s):
        return 'Record'

    return 'Rank'


VALID_SCORES = ('2-0', '2-1', '1-2', '0-2', '1-0', '0-1')
VALID_SCORES_SPLIT = tuple(tuple(s.split('-')) for s in VALID_SCORES)

score_replace = [('Z', '2'), ('Q', '0'), ('_', '-'), ('L', '1'), ('_', '-'), ('4', '-1'), ('-.', '-')]


def get_best_game_score(score: str):
    for a, b in score_replace:
        score = score.replace(a, b)

    if score == '':
        return '', ''

    if len(score) == 2:
        score = '-'.join(score)

    if len(score) == 3:
        score = score[0] + '-' + score[2]

    if score not in VALID_SCORES:
        return '', ''

    return score.split('-')


def correct_detection(df):
    """
    Correct ocr detection depending on column type.
    """
    df_ = []
    for col in df:
        t = column_type(col)
        if t == 'Name':
            df_.append([get_best_match_username(name)[0][0] for name in col])
        elif t == 'Record':
            s0, s1 = zip(*[get_best_match_score_multi(score) for score in col])
            df_.append(s0)
            df_.append(s1)
        elif t == 'Score':
            s0, s1 = zip(*[get_best_game_score(score) for score in col])
            df_.append(s0)
            df_.append(s1)
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


def clean_special_character(df):
    """
    Remove special character to csv.
    """
    df_ = []
    for col in df:
        df_.append([])
        for s in col:
            df_[-1].append(str(s).replace(',', '').replace('"', '').replace('\'', ''))
    return df_


def generate_csv_grid(path, df):
    try:
        with open(path, 'w') as file:
            for row in zip(*clean_special_character(df)):
                file.write(','.join(row) + '\n')
    except PermissionError:
        print('Please close output.csv')


def load_image(image_path):
    """
    Load image and apply pre-treatment.
    """
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    ratio = 2
    width = int(ratio * img.shape[1])
    height = int(ratio * img.shape[0])
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh, im_bw = cv2.threshold(gray_image, 165, 255, cv2.THRESH_BINARY)
    return resized, im_bw


def run_easyocr_multi(image_path=IMAGE_PATH, output_csv="output.csv", output_image='image-displayed.png'):
    img, im_bw = load_image(image_path)

    reader = easyocr.Reader(['en'])
    results = reader.readtext(im_bw)

    df, args = process_results(results, im_bw.shape)
    generate_csv_grid(output_csv, df)

    img_res = display_result(img, *args)
    cv2.imwrite(output_image, img_res)
