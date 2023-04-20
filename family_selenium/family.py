import json
from dataclasses import asdict
from datetime import datetime

import bs4
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import JavascriptException
import httpx
import dotenv
import os
from typing import Dict, Any, List, Tuple
import rich

try:
    from family_selenium.entities import User, Family, Member, Risks
    from family_selenium.utils import get_headers, get_risk_dict,\
        FamilyNotFound, FamilyNotInList, is_valid_iin, WrongIIN
except (ModuleNotFoundError, ImportError):
    from entities import User, Family, Member, Risks
    from utils import get_headers, get_risk_dict,\
        FamilyNotFound, FamilyNotInList, is_valid_iin, WrongIIN


def get_token(user: User, base_url: str) -> Dict:
    url = f'{base_url}/auth/login'

    headers = get_headers()

    response = httpx.post(
        url=url,
        json={'username': user.username, 'password': user.password},
        headers=headers
    )
    response.raise_for_status()

    return response.json()


def auth(driver: WebDriver) -> None:
    driver.get('http://10.61.164.228/#/login')
    driver.implicitly_wait(10)

    username_field, password_field = driver.find_elements(By.TAG_NAME, 'input')
    submit_button = driver.find_element(By.CSS_SELECTOR, '.px-4')

    username_field.send_keys('USER217')
    password_field.send_keys('As123456+')
    submit_button.click()


def set_local_storage(driver: WebDriver, storage: Dict) -> None:
    access_token = storage['accessToken']
    refresh_token = storage['refreshToken']
    user_auth = json.dumps(storage['user'], ensure_ascii=False)
    script = f"localStorage.setItem('accessToken', '{access_token}');"
    script += f"localStorage.setItem('refreshToken', '{refresh_token}');"
    script += f"localStorage.setItem('userAuth', '{user_auth}');"
    driver.execute_script(script)


def get_env_vars() -> Tuple[str, str, str]:
    dotenv.load_dotenv()
    base_url, username, password = os.getenv('URL'), os.getenv('USR'), os.getenv('PSW')
    if not bool(base_url and username and password):
        raise ValueError('One of the variables or .env file does not exist')
    return base_url, username, password


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


def convert_value(val: str) -> Any:
    if next((True for c in val if c.isalpha()), False):
        return val.strip()
    val = val.replace(' ', '')
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val


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

    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
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
    data = get_family_data(iin='444444444444')
    rich.print(data)
