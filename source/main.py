import asyncio
import datetime
import json
import os
import time
import warnings
from dataclasses import dataclass
from typing import Dict, List
import httpx
import pandas as pd
from dotenv import load_dotenv
from tqdm.auto import tqdm


@dataclass
class User:
    username: str
    password: str
    token: str = None
    user_id: str = None


@dataclass
class Family:
    member_count: int = None
    child_count: int = None
    family_level: str = None
    address: str = None
    salary: int = None
    social_payment: int = None
    pc_income: int = None
    total_income: int = None
    income: str = None
    land_number: int = None
    emp_number: int = None


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


def test(user, base_url, iin):
    url = f'{base_url}/api/card/familyInfo'

    payload = {'iin': iin}
    headers = get_headers()
    headers['Authorization'] = f'Bearer {user.token}'

    response = httpx.post(url=url, json=payload, headers=headers)

    data = response.json()

    for i, family_member in enumerate(data.get('familyMemberList'), 1):
        member_full_name = family_member.get('fullName')
        print(f'textbox_family_{i}: {member_full_name}')

    # ✅✅✅ Кол-во человек: numericinput_number_of_family ✅✅✅
    member_count = data.get('family').get('familyQuality').get('cntMem')

    # ✅✅✅ Кол-во детей: numericinput_number_of_child ✅✅✅
    child_count = data.get('family').get('familyQuality').get('cntChild')

    # ✅✅✅ Уровень семьи: textbox_level_fam ✅✅✅
    family_level = data.get('family').get('familyQuality').get('tzhsDictionary').get('nameRu')

    # ✅✅✅ Адрес: textbox_address ✅✅✅
    address = data.get('addressRu')

    # ❓❓❓ Зарплата: numericinput_salary TODO
    salary = data.get('family').get('familyQuality').get('incomeAsp')

    # ❓❓❓ Социальные выплаты: numericinput_cots_vyplaty TODO
    social_payment = data.get('family').get('familyQuality').get('incomeCbd')

    # ❓❓❓ Среднедушевой доход: numericinput_cots_income TODO
    pc_income = data.get('family').get('familyQuality').get('sdd')

    # ❓❓❓ Совокупный доход для АСП: numericinput_income_ASP TODO

    # ❓❓❓ Среднедушевой доход для АСП: numericinput_mid_income_ASP TODO
    total_income = data.get('family').get('familyQuality').get('sddAsp')

    # ❓❓❓ Доход: textbox_income TODO
    income = data.get('family').get('familyQuality').get('familyPm').get('nameRu')

    # ❓❓❓ Рекомендации: check_rec TODO

    # ✅✅✅ Жилая недвижимость: textbox_count_home ✅✅✅
    land_number = data.get('family').get('familyQuality').get('cntLand')

    # ✅✅✅ Кол-во трудоустроенных членов семьи: textbox_worker_fam ✅✅✅
    emp_number = data.get('family').get('familyQuality').get('cntEmp')

    # Получатели социальных выплат: textbox_count_cots_income

    # Риски: textbox_risks

    # textbox_risks_1

    # textbox_risks_2

    # textbox_risks_3

    # textbox_risks_4

    # Член многодетной семьи: numericinput_have_many_ch

    # Дети до 18 лет: numericinput_ch_eightn

    # Наемные работники: numericinput_naemniki

    # Многодетные семьи: numericinput_count_ch_large

    # Получатель пособий: numericinput_akimat_give

    family = Family(
        member_count=member_count,
        child_count=child_count,
        family_level=family_level,
        address=address,
        salary=salary,
        social_payment=social_payment,
        pc_income=pc_income,
        total_income=total_income,
        income=income,
        land_number=land_number,
        emp_number=emp_number,
    )


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print("Elapsed time: {:.4f} seconds".format(elapsed_time))

    return wrapper


class AsyncTest:
    def __init__(self, user, base_url, iins):
        self.base_url = base_url
        self.iins = iins[:100]
        self.results = []
        self.errored = []
        self.headers = get_headers()
        self.headers['Authorization'] = f'Bearer {user.token}'
        self.headers['Content-Type'] = 'application/json'
        self.pbar = tqdm(total=len(self.iins), colour='green')

    async def get_family_data(self, client: httpx.AsyncClient, iin: int):
        payload = {'iin': iin}
        _ = await client.post(f'{self.base_url}/api/card/familyInfo', json=payload)
        self.pbar.update(1)

    async def run(self):
        client = httpx.AsyncClient(headers=self.headers, timeout=None)
        async with client:
            tasks = [self.get_family_data(client, iin) for iin in self.iins]
            await asyncio.gather(*tasks)
        self.pbar.close()


@timer
def async_test(user: User, base_url: str, iins: list):
    async_obj = AsyncTest(user=user, base_url=base_url, iins=iins)
    asyncio.run(async_obj.run())


def main():
    load_dotenv()

    start_time = datetime.datetime.now().strftime('%Y-%m-%d')

    user = User(username=os.getenv('USR'), password=os.getenv('PSW'))
    base_url = os.getenv('URL')

    try:
        auth_data = auth(user=user, base_url=base_url)
    except (TimeoutError, httpx.ConnectTimeout) as e:
        print('No VPN connection...')
        return

    user.token = auth_data['accessToken']
    user.user_id = str(auth_data['user']['userId'])

    # person_list_file = get_excel_file_path()
    # if not person_list_file:
    #     excel_data = get_person_list(user=user, base_url=base_url)
    #     with open(fr'D:\Work\python_rpa\arta_profiles\person_list\person_list__{start_time}.xlsx', 'wb') as output:
    #         output.write(excel_data)

    iins = get_iins()

    # test(user, base_url, iins[0])

    async_test(user=user, base_url=base_url, iins=iins)

    pass


if __name__ == '__main__':
    main()
