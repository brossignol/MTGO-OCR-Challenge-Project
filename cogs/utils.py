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

SCORES = []
for i in range(0, 15):
    for j in range(0, 15):
        SCORES.append(f'{i}-{j}')
SCORES.append('1-1-1')
SCORES.append('2-1-1')
SCORES.append('2-1-2')
SCORES.append('2-1-3')


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
        return (best_matches, 'pass')
    elif len(best_matches) > 1:
        return (best_matches, 'mixed')
    else:
        return ([username], 'fail')
