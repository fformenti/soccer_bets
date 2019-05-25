
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime as dt

page = 'https://esporte.uol.com.br/futebol/campeonatos/brasileirao/jogos/'
driver = webdriver.Chrome('/Users/felipeformenti/dev/webdrivers/chromedriver')
#driver = webdriver.Firefox('/Users/felipeformenti/dev/webdrivers/chromedriver')
driver.get(page)

html = driver.page_source
soup = BeautifulSoup(html)

# Day of the week dict
dow_dict = {
    'Seg': 'Monday',
    'Ter': 'Tuesday',
    'Qua': 'Wednesday',
    'Qui': 'Thursday',
    'Sex': 'Friday',
    'Sáb': 'Saturday',
    'Dom': 'Sunday'
}

# check out the docs for the kinds of things you can do with 'find_all'
# this (untested) snippet should find tags with a specific class ID
# see: http://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class
listao = list()
last_round = 34
for rodadas_impar in soup.find_all("li", class_="confrontos-10 odd "):
    rodada_str = rodadas_impar.text.replace('pós-jogo', '')
    rodada_str_clean = ' '.join(rodada_str.split())
    rodada_list = rodada_str_clean.split()
    rodada_num = rodada_list[1]
    if int(rodada_num) <= last_round:
        rodada_list = rodada_list[2:]
        rodada = list(zip(*[iter(rodada_list)] * 8))
        final = [(*k, rodada_num) for k in rodada]
        listao.extend(final)

for rodadas_par in soup.find_all("li", class_="confrontos-10 even "):
    rodada_str = rodadas_par.text.replace('pós-jogo', '')
    rodada_str_clean = ' '.join(rodada_str.split())
    rodada_list = rodada_str_clean.split()
    rodada_num = rodada_list[1]
    if int(rodada_num) <= last_round:
        rodada_list = rodada_list[2:]
        rodada = list(zip(*[iter(rodada_list)] * 8))
        final = [(*k, rodada_num) for k in rodada]
        listao.extend(final)

df = pd.DataFrame(listao, columns=['home_goals', 'home_team', 'away_goals', 'away_team', 'dow',
                                   'date', 'foo', 'time', 'round'])


def outcome_f(x, y):
    if x > y:
        return 1
    if y > x:
        return -1
    return 0

df.drop('foo', axis=1, inplace=True)
df['outcome'] = list(map(lambda x, y: outcome_f(x, y), df['home_goals'], df['away_goals']))
df['home_points'] = np.where(df['outcome'] > 0, 3, np.where(df['outcome'] < 0, 0, 1))
df['away_points'] = np.where(df['outcome'] > 0, 0, np.where(df['outcome'] < 0, 3, 1))
df['round'] = pd.to_numeric(df['round'])

home_df = df[['home_team', 'home_points', 'round']]
home_df.rename(index=str, columns={'home_team': 'team', 'home_points': 'points'}, inplace=True)
away_df = df[['away_team', 'away_points', 'round']]
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

df = df.merge(rolling_hist, how='left', left_on=['home_team', 'round'], right_on=['team', 'round'])
df.rename(index=str, columns={'last3': 'home_last3', 'last6': 'home_last6', 'total_points': 'home_total_points'},
          inplace=True)

df = df.merge(rolling_hist, how='left', left_on=['away_team', 'round'], right_on=['team', 'round'])
df.rename(index=str, columns={'last3': 'away_last3', 'last6': 'away_last6', 'total_points': 'away_total_points'},
          inplace=True)

df = df.merge(home_df, how='left', left_on=['home_team', 'round'], right_on=['team', 'round'], copy=False)
df = df.merge(away_df, how='left', left_on=['away_team', 'round'], right_on=['team', 'round'], copy=False)


model_df = df[['home_team', 'away_team', 'home_total_points', 'away_total_points', 'home_last3', 'home_last6',
               'away_last3', 'away_last6','total_points_at_home', 'last3_at_home', 'total_points_at_away',
               'last3_at_away', 'dow', 'time']]


model_df['time'] = model_df['time'].apply(lambda x: dt.time(int(x[:2]), int(x[-2:])))
model_df['dow'] = model_df['dow'].apply(lambda x: dow_dict[x])

