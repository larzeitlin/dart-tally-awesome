import pandas as pd
import sqlalchemy
from datetime import datetime, timedelta
import math

def expected_score(RA, RB):
    EA = 1 / (1 +  (math.pow(10, ((RB - RA)/400))))
    return(EA)

def calculate_new_elo_scores(elo_scores, day_games, K=20):
    for index, row in day_games.iterrows():
        winner_exp = expected_score(elo_scores[row["winner_id"]], row['looser_id'])
        looser_exp = 1 - winner_exp
        winner_new_elo = elo_scores[row['winner_id']] + K * (row['winner_score'] - winner_exp)
        looser_new_elo = elo_scores[row['looser_id']] + K * (row['looser_score'] - looser_exp)
        elo_scores[row['winner_id']] = winner_new_elo
        elo_scores[row['looser_id']] = looser_new_elo
    return(elo_scores)

def make_elo_scores_df(game_log_df, player_ids_df, K=20):
    start_date = min(game_log_df['created_at'] - timedelta(days=1)).date()
    end_date = max(game_log_df['created_at'] + timedelta(days=1)).date()
    date_range = [start_date + timedelta(days=x) for x in range(0, (end_date - start_date).days)]
    player_ids = player_ids_df['player_id'].tolist()
    out_df = pd.DataFrame(index=date_range, columns=player_ids)
    elo_scores = {i : 100 for i in player_ids}
    for index, row in out_df.iterrows():
        day_games = game_log_df[game_log_df['created_at'].dt.date == index]
        if day_games.shape[0] == 0:
            out_df.at[index] = elo_scores
        else:
            elo_scores = calculate_new_elo_scores(elo_scores, day_games, K)
            out_df.at[index] = elo_scores
    return(out_df)
