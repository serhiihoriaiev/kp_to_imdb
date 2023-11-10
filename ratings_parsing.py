import re
import json
import pickle
from bs4 import BeautifulSoup

if __name__ == '__main__':

    html_lst = pickle.load(open("ratings_html.p", "rb"))
    res_films = []
    res_shows = []
    # with open("film_table.html", "w") as f:
    #     f.write(html_lst[2])

    with open('parsed_ratings.txt', 'w', encoding='utf-8') as f:
        for page in html_lst:
            soup = BeautifulSoup(page, 'html.parser')
            film_elements = soup.find_all('div', class_='item')
            for film in film_elements:
                name_eng = film.find('div', class_='nameEng')
                name_rus = film.find('div', class_='nameRus')
                result_dict = {}

                result_dict['date'] = film.find('div', class_='date').text
                result_dict['name'] = (name_eng.text 
                                    if name_eng.text != '\xa0' 
                                    else re.match(r'^(.+?)\s*\((:?\d{4}|сериал)', name_rus.text).group(1))
                result_dict['name'] = result_dict['name'].replace('\xa0', ' ')
                if result_dict['name'] and ', The' in result_dict['name']:
                    result_dict['name'] = re.sub(r'(.+), The', r'The \1', result_dict['name'])
                elif result_dict['name'] and ', [Dd]as' in result_dict['name']:
                    result_dict['name'] = re.sub(r'(.+), [Dd]he', r'Das \1', result_dict['name'])
                
                if 'сериал' in name_rus.text:
                    result_dict['year'] = re.search(r'сериал,\s*(\d{4})', name_rus.text).group(1)
                    result_dict['show'] = True
                else:
                    result_dict['year'] = re.search(r'\((\d{4})', name_rus.text).group(1)
                    result_dict['show'] = False
                result_dict['rating'] = re.search(r"rating:\s*'(\d*)", film.decode_contents()).group(1)             
                
                f.write(json.dumps(result_dict) + ',\n')