from bs4 import BeautifulSoup as bs
import requests
import requests
from cookies import Cookies
from matplotlib import pyplot as plt
import pandas as pd


def parse_for_cars(soup):
    """Parsers search results, returns dics of cars"""
    result = []
    hondas = soup.find_all('h2', {'class': ['mb-0']})
    milages = soup.find_all('span', {'class': ['icon-meter', 'text-cool-gray-40', 
                                            'key-point-icon', 'd-inline-block', 
                                            'size-12', 'mr-0_5'],
                                    'title': 'Car Mileage'})
    data = zip(hondas, milages)
    for car, info in data:
        if not car or not info: continue
        if 'heading-3' in car['class']: continue
        car_data = {}
        car_data['url'] = 'https://www.edmunds.com'+car.a['href']
        price, *name = car.a.attrs['aria-label'].split()
        price = int(''.join(price.lstrip('$').split(','))) if '$' in price else ''
        year, name = name[0], ' '.join(name[1:])
        year = int(year) if year.isdigit() else ''
        miles = ''.join(info.next.text.split()[0].split(','))
        miles = int(miles) if miles.isdigit() else ''
        if not price or not year or not miles: continue
        car_data['year'], car_data['name'], car_data['price'], car_data['miles'] = year, name, price, miles
        result.append(car_data)
    return result


def request_cars(url):
    """Returns a soup give a url"""
    cookies = Cookies.edmunds_cookies
    headers = Cookies.edmunds_headers
    response = requests.get(url,
                        cookies=cookies,
                        headers=headers).text
    return bs(response, 'html.parser')



def get_cars(year=2009, model='accord', radius=25):
    """This function makes the initial request"""
    result = []
    if model not in ['accord', 'civic']: raise ValueError('only civic or accord')
    cookies = Cookies.edmunds_cookies
    headers = Cookies.edmunds_headers
    params = {
        'inventorytype': 'used,cpo',
        'make': 'honda',
        'model': f'honda|{model}',
        'year': f'{year}-{year}',
        'radius': str(radius)
    }
    response = requests.get('https://www.edmunds.com/inventory/srp.html',
                        params=params, 
                        cookies=cookies, 
                        headers=headers)
    html = response.text
    soup = bs(html, 'html.parser')
    parsed_cars = parse_for_cars(soup)
    pages = soup.find_all('a', {'class': ['pagination-element', 'num-link', 
                                          'mx-1_25', 'text-blue-30']})[1:-1]
    for page in pages:
        url = 'https://www.edmunds.com' + page.attrs['href']
        soup = request_cars(url)
        parsed_cars.extend(parse_for_cars(soup))
    return parsed_cars

def parse_edmunds(years=range(2010,2012), model='accord', radius=25):
    cars = []
    for y in years:
        cars.extend(get_cars(y, model=model, radius=radius))
    df = pd.DataFrame.from_dict(cars)
    return df

