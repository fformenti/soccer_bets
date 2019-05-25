from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd



def parse_2017():
    html = open("data/brasileiro_2017", "r", encoding='utf-8')
    soup = BeautifulSoup(html)
    # Close file
    #Html_file.close()

    list_of_matches = list()
    for round_ in soup.find_all("div", class_="swiper-slide"):
        round_number = round_.h3.text
        for match_ in round_.find_all("li", class_="item"):
            date_time = match_.find("span", class_="date-time").text.split()
            teams = match_.find_all("span", class_="shortname")
            goals = match_.find_all("span", class_="goal")
            game_date = dt.datetime.strptime(date_time[0] + '/2017', '%d/%m/%Y')
            match_info = [goals[0].text, teams[0].text, goals[1].text, teams[1].text, game_date.weekday(), game_date,'-',
                          date_time[2], round_number]
            list_of_matches.append(match_info)
    return list_of_matches

def parse_2018(round):
    html = open("data/brasileiro_2018", "r", encoding='utf-8')
    soup = BeautifulSoup(html)
    # Close file
    #Html_file.close()
    rounds_= soup.find_all("li", class_="confrontos-10 odd ")
    rounds_.extend(soup.find_all("li", class_="confrontos-10 odd "))

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



list_of_matches = list()
list_of_matches.extend(parse_2017())
list_of_matches.extend(parse_2018())


df = pd.DataFrame(list_of_matches, columns=['home_goals', 'home_team', 'away_goals', 'away_team', 'dow',
                                   'date', 'foo', 'time', 'round'])

df.to_csv('data/historico.csv', index=False)