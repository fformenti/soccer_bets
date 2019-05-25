import pandas as pd
import numpy as np

def outcome_f(x, y):
    if x > y:
        return 1
    if y > x:
        return -1
    return 0


matches = pd.read_csv('data/historico.csv')


matches.drop('foo', axis=1, inplace=True)
matches['outcome'] = list(map(lambda x, y: outcome_f(x, y), matches['home_goals'], matches['away_goals']))
matches['home_points'] = np.where(matches['outcome'] > 0, 3, np.where(matches['outcome'] < 0, 0, 1))
matches['away_points'] = np.where(matches['outcome'] > 0, 0, np.where(matches['outcome'] < 0, 3, 1))
matches['round'] = pd.to_numeric(matches['round'])

home_df = matches[['home_team', 'home_points', 'round']]
home_df.rename(index=str, columns={'home_team': 'team', 'home_points': 'points'}, inplace=True)
away_df = matches[['away_team', 'away_points', 'round']]
away_df.rename(index=str, columns={'away_team': 'team', 'away_points': 'points'}, inplace=True)

home_df.sort_values(by=['team', 'round'], ascending=[True, True], inplace=True)
home_df['points_lag1'] = home_df.groupby(['team'])['points'].shift(1)
home_df['total_points_at_home'] = home_df.groupby('team')['points_lag1'].transform(pd.Series.cumsum)
last3 = home_df.groupby('team')['points_lag1'].rolling(min_periods=3, window=3).sum()
#home_df['last3_at_home'] = list(map(lambda x, y: x - y, last3_and_current, home_df['points']))
home_df['last3_at_home'] = list(last3)
home_df.drop(['points', 'points_lag1'], axis=1, inplace=True)

away_df.sort_values(by=['team', 'round'], ascending=[True, True], inplace=True)
away_df['points_lag1'] = away_df.groupby(['team'])['points'].shift(1)
away_df['total_points_at_away'] = away_df.groupby('team')['points'].transform(pd.Series.cumsum)
last3 = away_df.groupby('team')['points'].rolling(min_periods=3, window=3).sum()
#away_df['last3_at_away'] = list(map(lambda x, y: x - y, last3_and_current, away_df['points']))
away_df['last3_at_away'] = list(last3)
away_df.drop(['points', 'points_lag1'], axis=1, inplace=True)

rolling_hist = pd.concat(home_df[['team', 'points', 'round']], away_df[['team', 'points', 'round']])
rolling_hist.sort_values(by=['team', 'round'], ascending=[True, True], inplace=True)
rolling_hist['points_lag1'] = rolling_hist.groupby(['team'])['points'].shift(1)
rolling_hist['total_points'] = rolling_hist.groupby('team')['points'].transform(pd.Series.cumsum)

last3 = rolling_hist.groupby('team')['points_lag1'].rolling(min_periods=3, window=3).sum()
rolling_hist['last3'] = list(last3)
#rolling_hist['last3'] = list(map(lambda x, y: x - y, last3_and_current, rolling_hist['points']))

last6 = rolling_hist.groupby('team')['points_lag1'].rolling(min_periods=6, window=6).sum()
rolling_hist['last3'] = list(last6)
#rolling_hist['last6'] = list(map(lambda x, y: x - y, last6_and_current, rolling_hist['points']))

rolling_hist.drop(['points, points_lag1'], axis=1, inplace=True)

model_df = matches.merge(rolling_hist, how='left', left_on=['home_team', 'round'], right_on=['team', 'round'])
model_df.rename(index=str, columns={'last3': 'home_last3', 'last6': 'home_last6', 'total_points': 'home_total_points'},
          inplace=True)

model_df = model_df.merge(rolling_hist, how='left', left_on=['away_team', 'round'], right_on=['team', 'round'])
model_df.rename(index=str, columns={'last3': 'away_last3', 'last6': 'away_last6', 'total_points': 'away_total_points'},
          inplace=True)

model_df = model_df.merge(home_df, how='left', left_on=['home_team', 'round'], right_on=['team', 'round'], copy=False)
model_df = model_df.merge(away_df, how='left', left_on=['away_team', 'round'], right_on=['team', 'round'], copy=False)


model_df = model_df[['home_team', 'away_team', 'home_total_points', 'away_total_points', 'home_last3', 'home_last6',
               'away_last3', 'away_last6','total_points_at_home', 'last3_at_home', 'total_points_at_away',
               'last3_at_away', 'dow', 'time']]


model_df['time'] = model_df['time'].apply(lambda x: model_df.time(int(x[:2]), int(x[-2:])))
model_df['dow'] = model_df['dow'].apply(lambda x: dow_dict[x])