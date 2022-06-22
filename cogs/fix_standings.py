"""
This function aim to fix full standings directly into the Google sheet:
* fix usernames matching with reference
* fill missing score with symmetric

The Google sheet is expected to have:
 * A list of reference name
 * Standings must be formatted along with:
      "Rank, Name, Record-win, Record-loss, Round, Games-win, Games-loss, Round, Games-win, Games-loss, etc"
"""
from cogs.ocr_multicolumn import generate_csv_grid
from cogs.sheetapi import get_sheet_by_url
from cogs.utils import get_best_match_username_standings


def get_ref_names(sheet, tab='Input', col=2):
    """
    Get list of reference usernames. i.e. correct list of player playing this challenge.
    """
    ws = sheet.worksheet(tab)
    ref_names = set(ws.col_values(col))

    warning = None
    if '' in ref_names:
        warning = 'Names are missings in Input tab'
    ref_names.discard('')
    ref_names.discard('Player')
    ref_names.add('(Bye)')

    return ref_names, warning


def get_standings(sheet, tab='Standings', range='N:BD'):
    ws = sheet.worksheet(tab)
    values = ws.get_values(range)
    return list(zip(*values))


def fix_names(standings, ref_names):
    """
    Force matching with Input names
    """
    ref_names = {name.lower(): name for name in ref_names}

    fixed = []
    fixed_names = set()
    missing_names = set()
    for col in standings:
        if col[0] in ('Name', 'Round'):
            fixed.append([col[0]])
            for name in col[1:]:
                r, matched = get_best_match_username_standings(name, ref_names)
                fixed[-1].append(r)
                if not matched and name != '':
                    missing_names.add(name)
                if name != r:
                    fixed_names.add(f'{name} -> {r}')
        else:
            fixed.append(col)
    return fixed, missing_names, fixed_names


def group_games_score(standings):
    """Group by first player, round"""
    matches = dict()
    positions = dict()
    for i, line in enumerate(standings[1:]):
        player0 = str(line[1])
        for j in range(4, len(line), 3):
            rounds = j // 3
            positions[(player0, rounds)] = (i + 1, j)
            player1 = str(line[j])
            if player1 != '(Bye)':
                score = tuple(line[j + 1: j + 3])
                matches.setdefault((player0, rounds), []).append([player1, score])
                if player1 != '':
                    matches.setdefault((player1, rounds), []).append([player0, score[::-1]])
    return matches, positions


VALID_SCORES = ('2-0', '2-1', '1-2', '0-2', '1-0', '0-1')
VALID_SCORES_SPLIT = tuple(tuple(s.split('-')) for s in VALID_SCORES)


def fix_score(standings):
    """
    Fix missing score by looking at the symmetric.
    """
    standings = list(map(list, zip(*standings)))
    matches, positions = group_games_score(standings)

    fixed_scores = set()
    missing_score = set()
    missings = []
    multiples = []
    for (p0, rd), vs in matches.items():
        if (p0, rd) not in positions:
            missings.append(f'Missing matches of {p0} round {rd}')
            continue
        i, j = positions[(p0, rd)]

        if len(vs) == 0:
            missings.append(f'Missing matches of {p0} round {rd}')
            continue

        if len(vs) > 2:
            p1s = [v[0] for v in vs]
            multiples.append(f'Multiple score of {p0} vs {p1s} round {rd}')
            continue

        p1s, ss = zip(*vs)

        # get valid score
        valid_s = set(ss).intersection(VALID_SCORES_SPLIT)
        if len(valid_s) > 1:
            multiples.append(f'Multiple score of {p0} round {rd}: ({valid_s})')
            s = None
        elif len(valid_s) == 1:
            s = next(iter(valid_s))
        else:
            s = None

        # get valid opponent
        valid_p1 = set(p1s).difference({''})
        if len(valid_p1) > 1:
            multiples.append(f'Multiple opponent {p0} vs {valid_p1} round {rd}')
            p1 = None
        elif len(valid_p1) == 1:
            p1 = next(iter(valid_p1))
        else:
            p1 = None

        # warnings
        if p1 is None and s is not None:
            missings.append(f'Missing opponent of {p0} round {rd}')
        elif s is None and p1 is not None:
            missing_score.add(tuple(sorted((p0, p1)) + [rd]))  # do that to avoid double warning A vs B, B vs A

        if len(vs) == 1:
            p1, s = vs[0]
            if len(s) > 1:
                standings[i][j] = p1
                standings[i][j + 1] = s[0]
                standings[i][j + 2] = s[1]
        elif len(vs) == 2:
            # fix player
            if p1 is not None:
                if standings[i][j] != p1:
                    fixed_scores.add(f'{p0} round {rd} -> vs {p1}')
                standings[i][j] = p1

            # fix score
            if s is not None:
                if tuple(standings[i][j + 1:j + 3]) != s:
                    fixed_scores.add(f'{p0} round {rd} -> {s[0]} {s[1]}')
                standings[i][j + 1] = s[0]
                standings[i][j + 2] = s[1]

    for p0, p1, rd in missing_score:
        missings.append(f'Missing score of {p0} vs {p1} round {rd}')

    return standings, multiples, missings, fixed_scores


def fix_standings(url, output_csv='output.csv'):
    # probably can be improved by looking at relative position
    sheet = get_sheet_by_url(url)
    ref_names, warning_ref_name = get_ref_names(sheet)

    standings = get_standings(sheet)

    standings, missing_names, fixed_names = fix_names(standings, ref_names)
    standings, multiples, missing_score, fixed_scores = fix_score(standings)

    generate_csv_grid(output_csv, zip(*standings[1:]))

    message = []
    if warning_ref_name:
        message.append(warning_ref_name + '\n')
    if len(missing_names) > 0:
        message.append(f'* Missing names: {len(missing_names)}')
        message.extend(list(map(str, missing_names)))
    if len(multiples) > 0:
        message.append(f'\n* Multiple matches/scores: {len(multiples)}')
        message.extend(multiples)
    if len(missing_score) > 0:
        message.append(f'\n* Missing matches/scores: {len(missing_score)}')
        message.extend(missing_score)
    if len(fixed_names) > 0:
        message.append(f'\n* Fixed names: {len(fixed_names)}')
        message.extend(fixed_names)
    if len(fixed_scores) > 0:
        message.append(f'\n* Fixed scores: {len(fixed_scores)}')
        message.extend(fixed_scores)
    if len(message) == 0:
        message = ['Standings look good']

    return standings, '\n'.join(message)


