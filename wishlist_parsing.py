import re
import pickle
from bs4 import BeautifulSoup

if __name__ == '__main__':

    html_lst = pickle.load(open("wishlist_html.p", "rb"))
    res_films = []
    res_shows = []
    # with open("film_table.html", "w") as f:
    #     f.write(html_lst[0])

    with open('parsed_wishlist.txt', 'w', encoding='utf-8') as f:
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
                result_dict['year'] = re.findall(r'\((\d{4})', info.text)[0]

                if re.search(r'\(сериал\)', name.text):
                    # res_shows.append(result_dict)
                    result_dict['show'] = True
                else:
                    # res_films.append(result_dict)
                    result_dict['show'] = False

                f.write(str(result_dict) + ',\n')
            
