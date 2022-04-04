import os
import difflib

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
for i in range(15):
    for j in range(15):
        SCORES.append(f'{i}-{j}')

RANKS = [str(i) for i in range(1, 1025)]


def get_best_match_score(score):
    possibilities = SCORES
    n = 3
    cutoff = 0.75
    best_match = difflib.get_close_matches(score, possibilities, n, cutoff)
    if len(best_match) > 0:
        return best_match[0].replace('-', ',')
    else:
        return score


def get_best_match_username(username):
    possibilities = USERLIST
    n = 3
    cutoff = 0.75
    best_matches = difflib.get_close_matches(username, possibilities, n, cutoff)
    if len(best_matches) == 1:
        score = difflib.SequenceMatcher(None, username, best_matches[0]).ratio()
        if score == 1:
            return (best_matches, 'perfect')
        return (best_matches, 'pass')
    elif len(best_matches) > 1:
        return (best_matches, 'mixed')
    else:
        return ([username], 'fail')


def get_best_match_rank(rank):
    # fix common errors if they exist
    rank = rank.replace('l', '1').replace('O', '0').replace('I', '1').replace('i', '1')
    possibilities = RANKS
    n = 3
    cutoff = 0.75
    best_match = difflib.get_close_matches(rank, possibilities, n, cutoff)
    if len(best_match) > 0:
        return best_match[0]
    else:
        return rank


def sort_eascyocr_results(results, pixel_width):
    """This sorts the outputted results from easyOCR
    so that they are returned in a line by line fashion.
    This is done to handle corner cases where certain lines
    are misplaced in the output. This function was written
    by pproteus."""

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
