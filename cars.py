from bs4 import BeautifulSoup as bs
import requests
import requests
from cookies import Cookies
from matplotlib import pyplot as plt
import pandas as pd


def get_cars(year=2011, model='accord', radius='30'):
    result = []
    if model not in ['accord', 'civic']: raise ValueError('only civic or accord')
    cookies = Cookies.cars_cookies
    headers = Cookies.cars_headers
    response = requests.get(
    f'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]=honda&maximum_distance={str(radius)}&mileage_max=&models[]=honda-{model}&monthly_payment=&page_size=100&sort=best_match_desc&stock_type=all&year_max={year}&year_min={year}&zip=90025',
    cookies=cookies,
    headers=headers).text
    soup = bs(response, 'html.parser')
    cars = soup.find_all('a', {'class': ['vehicle-card-link', 'js-gallery-click-link'],
                               'data-linkname': 'vehicle-listing'})
    for car in cars:
        car_data = {}
        url = 'https://www.cars.com' + car.attrs['href']
        year, *name = car.next.next.next.text.split()
        year = int(year) if year.isdigit() else ''
        name = ' '.join(name)
        miles = car.next.next.next.next.next.next
        price = ''.join(miles.next.next.next.next.next.text.lstrip('$').split(','))
        miles = ''.join(miles.text.split()[0].split(','))
        price = int(price) if price.isdigit() else ''
        miles = int(miles) if miles.isdigit() else ''
        if not price or not miles: continue
        car_data['url'], car_data['year'],  car_data['name'], car_data['price'], car_data['miles'] = url, year, name, price, miles
        result.append(car_data)
    return result


def parse_cars(years=[2011], model='accord', radius=25):
    cars = []
    for y in years:
        cars.extend(get_cars(y, model=model, radius=radius))
    df = pd.DataFrame.from_dict(cars)
    return df
