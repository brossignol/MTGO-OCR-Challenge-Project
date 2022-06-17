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

    ref_names.discard('')
    ref_names.discard('Player')
    ref_names.add('(Bye)')

    return ref_names


def get_standings(sheet, tab='Standings', range='N:BD'):
    ws = sheet.worksheet(tab)
    values = ws.get_values(range)
    return list(zip(*values))


def fix_names(standings, ref_names):
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
                    fixed_names.add((name, r))
        else:
            fixed.append(col)
    return fixed, missing_names, fixed_names


def group_games_score(standings):
    matches = dict()
    for i, line in enumerate(standings[1:]):
        player0 = line[1]
        for j in range(4, len(line), 3):
            rounds = j // 3
            player1 = line[j]
            if player1 not in ('', '(Bye)'):
                k = tuple(sorted((player0, player1)) + [rounds])
                score = line[j + 1: j + 3]
                v = [score, i + 1, j]
                matches.setdefault(k, []).append(v)
    return matches


VALID_SCORES = ('2-0', '2-1', '1-2', '0-2', '1-0', '0-1')
VALID_SCORES_SPLIT = tuple(s.split('-') for s in VALID_SCORES)


def fix_score(standings):
    """
    Fix missing score by looking at the symmetric.
    """
    standings = list(map(list, zip(*standings)))
    matches = group_games_score(standings)

    fixed_scores = set()
    missing_scores = set()
    for k, vs in matches.items():
        if len(vs) == 1:
            missing_scores.add(k)
        elif len(vs) > 2:
            missing_scores.add(k)
        elif len(vs) == 2:
            s0 = vs[0][0]
            s1 = vs[1][0]
            if s0 != s1[::-1]:
                if s0 in VALID_SCORES_SPLIT:
                    i, j = vs[1][1:]
                    standings[i][j + 1] = s0[1]
                    standings[i][j + 2] = s0[0]
                    fixed_scores.add(k)
                elif s1 in VALID_SCORES_SPLIT:
                    i, j = vs[0][1:]
                    standings[i][j + 1] = s1[1]
                    standings[i][j + 2] = s1[0]
                    fixed_scores.add(k)
                else:
                    missing_scores.add(k)
    return standings, missing_scores, fixed_scores


def fix_standings(url, output_csv='output.csv'):
    # probably can be improved by looking at relative position
    sheet = get_sheet_by_url(url)
    ref_names = get_ref_names(sheet)

    standings = get_standings(sheet)

    standings, missing_names, fixed_names = fix_names(standings, ref_names)
    standings, missing_scores, fixed_scores = fix_score(standings)

    generate_csv_grid(output_csv, zip(*standings))

    message = [f'Missing_names: {len(missing_names)}']
    for m in missing_names:
        message.append(str(m))
    message.append(f'\nMissing_scores: {len(missing_scores)}')
    for m in missing_scores:
        message.append(f'{m[0]} vs {m[1]} round {m[2]}')
    message.append(f'\nFixed_names: {len(fixed_names)}')
    for m in fixed_names:
        message.append(f'{m[0]} -> {m[1]}')
    message.append(f'\nFixed_scores: {len(fixed_scores)}')
    for m in fixed_scores:
        message.append(f'{m[0]} vs {m[1]} round {m[2]}')

    return standings, '\n'.join(message)


