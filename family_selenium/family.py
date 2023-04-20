import json
from dataclasses import dataclass
from typing import Dict, Any, List

import bs4
import httpx
import rich
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

try:
    from family_selenium.utils import get_headers, is_valid_iin, get_env_vars, convert_value
    from family_selenium.custom_exceptions import FamilyNotFound, FamilyNotInList, WrongPassword, WrongIIN
except (ModuleNotFoundError, ImportError):
    from utils import get_headers, is_valid_iin, get_env_vars, convert_value
    from family_selenium.custom_exceptions import FamilyNotFound, FamilyNotInList, WrongPassword, WrongIIN


@dataclass
class User:
    username: str
    password: str


def get_token(user: User, base_url: str) -> Dict:
    response = httpx.post(
        url=f'{base_url}/auth/login',
        json={'username': user.username, 'password': user.password},
        headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def set_local_storage(driver: WebDriver, storage: Dict) -> None:
    access_token = storage['accessToken']
    refresh_token = storage['refreshToken']
    user_auth = json.dumps(storage['user'], ensure_ascii=False)
    script = f"localStorage.setItem('accessToken', '{access_token}');"
    script += f"localStorage.setItem('refreshToken', '{refresh_token}');"
    script += f"localStorage.setItem('userAuth', '{user_auth}');"
    driver.execute_script(script)


def get_member_data(iin: str, base_url: str, token: str) -> List[Dict[str, str]]:
    headers = get_headers()
    headers['Authorization'] = f'Bearer {token}'
    response = httpx.post(url=f'{base_url}/api/card/familyInfo', json={'iin': iin}, headers=headers)
    response.raise_for_status()
    family_data = response.json()

    if family_data['family'] is None:
        raise FamilyNotFound(iin=iin)

    member_data = [{'ИИН': member['iin'], 'ФИО': member['fullName']} for member in family_data['familyMemberList']]
    selected_member_info = next((i, member) for i, member in enumerate(member_data) if member['ИИН'] == iin)
    member_data.pop(selected_member_info[0])
    member_data.insert(0, selected_member_info[1])
    return member_data


def get_general_info(soup: bs4.BeautifulSoup) -> Dict[str, Any]:
    general_info = dict()
    rows = soup.select('div > strong, .row')

    lines = []
    for row in rows:
        text = row.get_text(separator=';')
        if text.count(';') > 1:
            continue
        lines.append(text.replace(':', '').strip())

    indices = [i for i, line in enumerate(lines)
               if line in ['Общие сведения', 'Доход за квартал', 'Рекомендации',
                           'Активы семьи', 'Риски', 'Социальные статусы (кол-во человек)']]

    for index, pos in enumerate(indices):
        if ';' in lines[pos + 1]:
            general_info[lines[pos]] = {line.split(';')[0].strip(): convert_value(line.split(';')[1])
                                        for line in lines[pos + 1: indices[index + 1] if index != len(indices) - 1 else len(lines)]}
        else:
            general_info[lines[pos]] = lines[pos + 1: indices[index + 1] if index != len(indices) - 1 else len(lines)]

    return general_info


def get_family_data(iin: str, driver: WebDriver) -> Any:
    if not is_valid_iin(iin=iin):
        raise WrongIIN(iin=iin)

    base_url, username, password = get_env_vars()
    user = User(username=username, password=password)
    auth_data = get_token(user=user, base_url=base_url)
    member_data = get_member_data(iin=iin, base_url=base_url, token=auth_data['accessToken'])

    driver.get(url=base_url)
    set_local_storage(driver, auth_data)
    driver.get(f'{base_url}/#/family/{iin}')
    driver.implicitly_wait(10)
    soup = bs4.BeautifulSoup(
        markup=driver.find_element(By.CLASS_NAME, 'col-md-9').get_attribute('innerHTML'),
        features='html.parser'
    )

    general_info = get_general_info(soup=soup)
    return {'Члены семьи': member_data, **general_info}


if __name__ == '__main__':
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    _driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    with _driver:
        data = get_family_data(iin='444444444444', driver=_driver)
    rich.print(data)
