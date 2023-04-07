import asyncio
import datetime
import json
import os
import warnings
from typing import Dict, List
import httpx
import pandas as pd
from dotenv import load_dotenv
from tqdm.auto import tqdm
from entities import User, Family
from utils import timer, get_headers


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
    person_list_dir = fr'D:\Work\python_rpa\arta_profiles\person_list'
    return next((os.path.join(person_list_dir, file)
                 for file in os.listdir(person_list_dir)
                 if file.endswith('.xlsx')), None)


def get_iins(person_list_file: str = None) -> List[int]:
    person_list_file = get_excel_file_path() if not person_list_file else person_list_file
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('always')
        person_list = pd.read_excel(person_list_file, engine='openpyxl')
    return person_list['ИИН'].tolist()


class AsyncTest:
    def __init__(self, base_url: str, token: str, iins: List[int], pbar: tqdm = None):
        self.base_url = base_url
        self.iins = iins[:100]
        # self.results = []
        # self.errored = []
        self.headers = get_headers()
        self.headers['Authorization'] = token
        self.headers['Content-Type'] = 'application/json'
        self.pbar = pbar

    async def get_family_data(self, client: httpx.AsyncClient, iin: int):
        payload = {'iin': iin}
        _ = await client.post(f'{self.base_url}/api/card/familyInfo', json=payload)
        if self.pbar:
            self.pbar.update(1)

    async def run(self):
        client = httpx.AsyncClient(headers=self.headers, timeout=None)
        async with client:
            tasks = [self.get_family_data(client, iin) for iin in self.iins]
            await asyncio.gather(*tasks)


@timer
def async_test(base_url: str, user: User, iins: list):
    token = f'Bearer {user.token}'
    with tqdm(total=len(iins), colour='green') as pbar:
        async_obj = AsyncTest(base_url=base_url, token=token, iins=iins, pbar=pbar)
        asyncio.run(async_obj.run())


def main():
    load_dotenv()

    start_time = datetime.datetime.now().strftime('%Y-%m-%d')

    user = User(username=os.getenv('USR'), password=os.getenv('PSW'))
    base_url = os.getenv('URL')

    # try:
    #     auth_data = auth(user=user, base_url=base_url)
    # except (TimeoutError, httpx.ConnectTimeout) as e:
    #     print('No VPN connection...')
    #     return

    # user.token = auth_data['accessToken']
    # user.user_id = str(auth_data['user']['userId'])

    user = User(username=user.username, password=user.password, token='dasfkajflkasjk')

    # person_list_file = get_excel_file_path()
    # if not person_list_file:
    #     excel_data = get_person_list(user=user, base_url=base_url)
    #     with open(fr'D:\Work\python_rpa\arta_profiles\person_list\person_list__{start_time}.xlsx', 'wb') as output:
    #         output.write(excel_data)

    # iins = get_iins()
    #
    # # test(user, base_url, iins[0])
    #
    # async_test(user=user, base_url=base_url, iins=iins)

    pass


if __name__ == '__main__':
    main()
