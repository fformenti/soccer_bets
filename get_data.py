from selenium import webdriver
import urllib.request

pages = ['https://esportes.estadao.com.br/classificacao/futebol/campeonato-brasileiro-serie-a/2017',
         'https://esporte.uol.com.br/futebol/campeonatos/brasileirao/jogos/']

year = 2017
for page in pages:
    driver = webdriver.Chrome('/Users/felipeformenti/dev/webdrivers/chromedriver')
    driver.get(page)
    html = driver.page_source

    # writing html to a file (exemplo 1)
    filename = "data/brasileiro" + year
    html_file = open(filename, "w", encoding='utf-8')
    html_file.write(html)
    html_file.close()
    year += year + 1

# writing page to txt file (exemplo 2)
# urllib.request.urlretrieve(page, "brasileiro_2017.txt")

