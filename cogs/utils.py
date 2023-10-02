import discord
from .config import SCORES, USERLIST, IMAGE_TYPES
import difflib


def get_best_match_score(score: str) -> str:
    possibilities = SCORES
    n = 3
    cutoff = 0.75
    best_match = difflib.get_close_matches(score, possibilities, n, cutoff)
    if len(best_match) > 0:
        return best_match[0].replace('-', ',')
    else:
        return score


def get_best_match_score_multi(score: str, possibilities=SCORES) -> (str, str):
    """
    return a pair of string (win, loss).
    """
    n = 3
    cutoff = 0.75
    best_match = difflib.get_close_matches(score, possibilities, n, cutoff)
    if len(best_match) > 0:
        return best_match[0].split('-')
    else:
        return score, ''


def get_best_match_username(username: str) -> tuple:
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
            return best_matches, 'perfect'
        return best_matches, 'fixed'
    elif len(best_matches) > 1:
        return best_matches, 'mixed'
    else:
        return [username], 'check'


def get_best_match_username_standings(name: str, possibilities):
    """
    Version to correct standings, more permissive on errors.
    """
    n = 3
    cutoff = 0.3
    best_match = difflib.get_close_matches(name.lower(), possibilities.keys(), n, cutoff)
    if len(best_match) > 0:
        return possibilities[best_match[0]], True
    else:
        return name, False


async def image_input_validation(ctx) -> bool:
    """Determines if input is valid."""
    try:
        image_url = ctx.message.attachments[0].url
        if image_url.split('?')[0].endswith(IMAGE_TYPES):
            await ctx.message.attachments[0].save("image.png")
            return True
        else:
            await ctx.send(embed=discord.Embed(
                                    title="Error",
                                    description="The attachment provided was not an image.",
                                    colour=discord.Color.blue()))
            return False
    except IndexError:
        await ctx.send(embed=discord.Embed(title="Error",
                                           description="No image attached.",
                                           colour=discord.Color.blue()))
        return False
