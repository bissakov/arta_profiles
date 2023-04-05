import asyncio
import datetime
import os
import time
import warnings
from dataclasses import dataclass
from typing import Dict, List
import httpx
import pandas as pd
from dotenv import load_dotenv


@dataclass
class User:
    username: str
    password: str
    token: str = None
    user_id: str = None


def get_headers() -> Dict:
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }


def auth(user: User, base_url: str) -> Dict:
    url = f'{base_url}/auth/login'

    headers = get_headers()
    headers['Content-Type'] = 'application/json'

    response = httpx.post(
        url=url,
        json={'username': user.username, 'password': user.password},
        headers=headers,
        timeout=120
    )

    return response.json()


def get_person_list(user: User, base_url: str) -> bytes:
    url = f'{base_url}/api/download/person-list-count'

    querystring = {'userId': user.user_id, 'countId': '93'}

    headers = get_headers()
    headers['Authorization'] = f'Bearer {user.token}'

    response = httpx.get(url=url, headers=headers, params=querystring, timeout=120)

    return response.content


def get_excel_file_path() -> str:
    person_list_dir = fr'D:\Work\python_rpa\arta\person_list'
    return next((os.path.join(person_list_dir, file)
                 for file in os.listdir(person_list_dir)
                 if file.endswith('.xlsx')), None)


def get_iins(person_list_file: str = None) -> List[int]:
    person_list_file = get_excel_file_path() if not person_list_file else person_list_file
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('always')
        person_list = pd.read_excel(person_list_file, engine='openpyxl')
    return person_list['ИИН'].tolist()


def main():
    load_dotenv()

    # start_time = datetime.datetime.now().strftime('%Y-%m-%d')
    #
    # user = User(username=os.getenv('USR'), password=os.getenv('PSW'))
    # base_url = os.getenv('URL')
    #
    # try:
    #     auth_data = auth(user=user, base_url=base_url)
    # except (TimeoutError, httpx.ConnectTimeout) as e:
    #     print('Отсутствует подключение к VPN')
    #     return
    #
    # user.token = auth_data['accessToken']
    # user.user_id = str(auth_data['user']['userId'])
    #
    # person_list_file = get_excel_file_path()
    # if not person_list_file:
    #     excel_data = get_person_list(user=user, base_url=base_url)
    #     with open(fr'D:\Work\python_rpa\arta\person_list\person_list__{start_time}.xlsx', 'wb') as output:
    #         output.write(excel_data)

    iins = get_iins()

    pass


if __name__ == '__main__':
    main()
