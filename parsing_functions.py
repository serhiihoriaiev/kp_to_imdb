import re
import json
import pickle
from bs4 import BeautifulSoup

def parse_watchlist(input_file="watchlist_html.p", output_file="parsed_watchlist.txt"):
    """
    Takes pickle file with watchlist HTML as an input and parses it's content into readable JSON
    """
    html_lst = pickle.load(open(input_file, "rb"))

    with open(output_file, 'w', encoding='utf-8') as f:
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
                    result_dict['show'] = True
                else:
                    result_dict['show'] = False

                f.write(json.dumps(result_dict) + ',\n')


def parse_ratings(input_file="ratings_html.p", output_file="parsed_ratings.txt"):
    """
    Takes pickle file with ratings HTML as an input and parses it's content into readable JSON
    """
    html_lst = pickle.load(open(input_file, "rb"))

    with open(output_file, 'w', encoding='utf-8') as f:
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