import re
import json
import pickle
from bs4 import BeautifulSoup

if __name__ == '__main__':

    html_lst = pickle.load(open("watchlist_html.p", "rb"))
    res_films = []
    res_shows = []
    # with open("film_table.html", "w") as f:
    #     f.write(html_lst[0])

    with open('parsed_watchlist.txt', 'w', encoding='utf-8') as f:
        for page in html_lst:
            soup = BeautifulSoup(page, 'html.parser')
            film_elements = soup.find_all('li', class_='item')
            for film in film_elements:
                result_dict = {}
                info_div = film.find('div', class_='info')
                name = info_div.find('a', class_='name')
                info = info_div.find('span')

                result_dict['ru_name'] = re.findall(r'^\(*[^\n(]+', name.text)[0].strip()
                result_dict['name'] = re.findall(r'^([^\s][^(]*)\s', info.text)[0] if re.match(r'^[^\s]', info.text) else None
                if result_dict['name'] and ', The' in result_dict['name']:
                    result_dict['name'] = re.sub(r'(.+), The', r'The \1', result_dict['name'])
                elif result_dict['name'] and ', [Dd]as' in result_dict['name']:
                    result_dict['name'] = re.sub(r'(.+), [Dd]he', r'Das \1', result_dict['name'])
                result_dict['year'] = re.findall(r'\((\d{4})', info.text)[0]

                if re.search(r'\(сериал\)', name.text):
                    # res_shows.append(result_dict)
                    result_dict['show'] = True
                else:
                    # res_films.append(result_dict)
                    result_dict['show'] = False

                f.write(json.dumps(result_dict) + ',\n')
            