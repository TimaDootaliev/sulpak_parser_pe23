"""  
1. Получить html код страницы
2. Получить карточки из html кода
3. Распарсить данные из карточек
4. Полученные данные записать в файл (json, csv)
"""
import csv
import json

# для отправки запросов
import requests
# для фильтрации html кода
from bs4 import BeautifulSoup

# для аннотации типов
from bs4 import Tag, ResultSet


HOST = 'https://www.sulpak.kg'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}


def get_html(url: str, category: str, headers: dict='', params: str=''):
    """ Функция для получения html кода """
    html = requests.get(
        url + '/f/' + category,
        headers=headers,
        params=params,
        verify=False 
    )
    return html.text


def get_card_from_html(html: str) -> ResultSet:
    """ Функция для получения карточек из html кода """
    soup = BeautifulSoup(html, 'lxml')
    cards: ResultSet = soup.find_all('li', class_='tile-container')
    return cards


def parse_data_from_cards(cards: ResultSet) -> list:
    """ Фильтрация данных из карточек """
    result = []
    for card in cards:
        try:
            image_link = card.find('picture').find('img').get('src')
        except AttributeError:
            image_link = 'Нет картинки'
        try:
            in_stock = card.find('span', class_='availability').text
        except AttributeError:
            in_stock = 'Нет в наличии'
        obj = {
            'brand': card.get('data-brand'),
            'title': card.get('data-name'),
            'price': float(card.get('data-price')),
            'image_link': image_link,
            'card_link': HOST+card.find('div', class_='goods-photo').find('a').get('href'),
            'in_stock': in_stock
        }
        result.append(obj)
    return result


def write_to_csv(data: list, file_name) -> None:
    """ Запись данных в csv файл """
    fieldnames = data[0].keys()
    with open(f'{file_name}.csv', 'w') as file:
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)


def write_to_json(data: list, file_name):
    with open(f'{file_name}.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_last_page(category):
    html = get_html(HOST, category)
    soup = BeautifulSoup(html, 'lxml')
    last_page = soup.find(class_='next').find_previous_sibling().text
    return int(last_page[-3:-1])


def main(category):
    result = []
    for page in range(get_last_page(category)+1):
        html = get_html(HOST, category, params=f'page={page}', headers=HEADERS)
        cards = get_card_from_html(html)
        list_of_cards = parse_data_from_cards(cards)
        result.extend(list_of_cards)
    write_to_csv(result, category)
    write_to_json(result, category)


if __name__ == '__main__':
    main('smartfoniy')
    # print(get_last_page('smartfoniy'))




# html = get_html(HOST, 'smartfoniy')
# # print(html)
# cards = get_card_from_html(html)
# # print(cards)
# data = parse_data_from_cards(cards)
# # print(data)
# write_to_csv(data, 'smartfoniy')
# write_to_json(data, 'smartfoniy')
