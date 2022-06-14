"""
This function aim to fix full standings directly into the Google sheet:
* fix usernames matching with reference
* fill missing score with symmetric

The Google sheet is expected to have:
 * A list of reference name
 * Standings must be formatted along with:
      "Rank, Name, Record-win, Record-loss, Round, Games-win, Games-loss, Round, Games-win, Games-loss, etc"
"""
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


def get_standings(sheet, tab='Standings', range='L:AS'):
    ws = sheet.worksheet(tab)
    values = ws.get_values(range)
    return list(zip(*values))


def fix_names(standings, ref_names):
    fixed = []
    messages = set()
    warnings = set()
    for col in standings:
        if col[0] in ('Name', 'Round'):
            fixed.append([col[0]])
            for name in col[1:]:
                r, matched = get_best_match_username_standings(name, ref_names)
                fixed[-1].append(r)
                if not matched:
                    warnings.add(f'missing name {name}')
                if name != r:
                    messages.add(f'{name} -> {r}')
        else:
            fixed.append(col)
    return fixed, warnings, messages


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
    standings = list(map(list, zip(*standings)))  # transposition
    matches = group_games_score(standings)

    messages = set()
    warnings = set()
    for k, vs in matches.items():
        if len(vs) != 2:
            print('fail', k, vs)
        else:
            s0 = vs[0][0]
            s1 = vs[1][0]
            if sorted(s0) != sorted(s1):
                print(k, vs)

                if s0 in VALID_SCORES_SPLIT:
                    i, j = vs[1][1:]
                    standings[i][j + 1] = s0[0]
                    standings[i][j + 2] = s0[1]
                    messages.add(f'fix score between {k[0]} and {k[1]}')
                elif s1 in VALID_SCORES_SPLIT:
                    i, j = vs[0][1:]
                    standings[i][j + 1] = s1[0]
                    standings[i][j + 2] = s1[1]
                    messages.add(f'fix score between {k[0]} and {k[1]}')
                else:
                    warnings.add(f'missing score between {k[0]} and {k[1]} round {k[2]}')
    return standings, warnings, messages


def fix_standing(url):
    sheet = get_sheet_by_url(url)
    ref_names = get_ref_names(sheet)

    standings = get_standings(sheet)

    standings, warnings_0, messages_0 = fix_names(standings, ref_names)
    standings, warnings_1, messages_1 = fix_score(standings)

    print(warnings_0, warnings_1)
    print(messages_0, messages_1)

    return standings


