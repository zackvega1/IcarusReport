# helpers.py

import csv
import math

def parse_matches(sets):
    matches = []
    for match in sets:
        if len(match['slots']) == 2:
            player1 = match['slots'][0]['entrant']['name']
            player1_id = match['slots'][0]['entrant']['id']
            player2 = match['slots'][1]['entrant']['name']
            player2_id = match['slots'][1]['entrant']['id']
            score = match.get('displayScore', 'N/A')
            round_name = match.get('identifier', 'Unknown Round')

            if score != 'N/A':
                player1_score, player2_score = parse_scores(score)
            else:
                player1_score, player2_score = 'N/A', 'N/A'

            matches.append((round_name, player1, player1_id, player1_score, player2, player2_id, player2_score))

    matches.sort(key=lambda x: (len(x[0]), x[0].upper()))
    return matches

def parse_scores(score):
    try:
        parts = score.split(' - ')
        p1_score = parts[0].split(' ')[-1]
        p2_score = parts[1].split(' ')[-1]
        return int(p1_score), int(p2_score)
    except:
        return 'N/A', 'N/A'

def export_to_csv(matches, filename='matches.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Player 1 Name', 'Player 1 ID', 'Player 1 Score', 'Player 2 Name', 'Player 2 ID', 'Player 2 Score'])
        for match in matches:
            writer.writerow([match[1], match[2], match[3], match[4], match[5], match[6]])

    print(f"Data successfully exported to {filename}")

def calculate_elo(player1_elo, player2_elo, player1_score, player2_score):
    K = 30
    expected_score1 = 1 / (1 + 10 ** ((player2_elo - player1_elo) / 400))
    expected_score2 = 1 / (1 + 10 ** ((player1_elo - player2_elo) / 400))

    if player1_score > player2_score:
        actual_score1, actual_score2 = 1, 0
    elif player1_score < player2_score:
        actual_score1, actual_score2 = 0, 1
    else:
        actual_score1, actual_score2 = 0.5, 0.5

    new_elo1 = player1_elo + K * (actual_score1 - expected_score1)
    new_elo2 = player2_elo + K * (actual_score2 - expected_score2)

    change1 = new_elo1 - player1_elo
    change2 = new_elo2 - player2_elo

    return new_elo1, new_elo2, change1, change2

def sort_matches_by_identifier(matches):
    def identifier_key(identifier):
        if len(identifier) == 1:
            return (1, ord(identifier.upper()) - ord('A'))
        else:
            result = []
            for char in identifier:
                if char.isalpha():
                    result.append(ord(char.upper()) - ord('A') + 1)
            return (2, *result)

    matches.sort(key=lambda match: identifier_key(match['identifier']))
    return matches

def sanitize_value(value):
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return 0
    return value
