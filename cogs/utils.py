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
for i in range(0, 15):
    for j in range(0, 15):
        SCORES.append(f'{i}-{j}')


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
    """This compares the username easyOCR read, with existing usernames
    in the userlist.txt file. This acts as a database lookup / autocorrect.
    This is accomplished using the difflib library which uses the Gestalt
    Pattern Matching approach. https://en.wikipedia.org/wiki/Gestalt_Pattern_Matching

    Possible outcomes are listed below:

    - perfect: 
        - easyOCR username has a similarity of 100% with an existing username.
    - fixed:
        - easyOCR username has a similarity greater than 75% with an existing username.
    - mixed:
        - easyOCR username has a similarity greater than 75% with multiple existing
          usernames.
    - check:
        - easyOCR username does not have a similarity greater than 75% with any
          existing usernames. This indicates either a new user, or a screw up
          on easyOCR's part."""

    possibilities = USERLIST
    n = 3
    cutoff = 0.75
    best_matches = difflib.get_close_matches(username, possibilities, n, cutoff)
    if len(best_matches) == 1:
        score = difflib.SequenceMatcher(None, username, best_matches[0]).ratio()
        if score == 1:
            return (best_matches, 'perfect')
        return (best_matches, 'fixed')
    elif len(best_matches) > 1:
        return (best_matches, 'mixed')
    else:
        return ([username], 'check')
