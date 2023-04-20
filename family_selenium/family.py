import json
from datetime import datetime
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
    from family_selenium.utils import get_headers, get_risk_dict, FamilyNotFound, FamilyNotInList
except (ModuleNotFoundError, ImportError):
    from entities import User, Family, Member, Risks
    from utils import get_headers, get_risk_dict, FamilyNotFound, FamilyNotInList


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


def get_env_vars() -> Tuple:
    dotenv.load_dotenv()
    base_url, username, password = os.getenv('URL'), os.getenv('USR'), os.getenv('PSW')
    if not bool(base_url and username and password):
        raise ValueError()
    return base_url, username, password


def get_family(driver: WebDriver) -> Family:
    family = Family()

    family_member_elements = driver.find_elements(By.CSS_SELECTOR, 'span.ms-2')
    family.members = [Member(full_name=member.text) for member in family_member_elements]

    box = driver.find_element(By.CLASS_NAME, 'col-md-9')
    rows = box.find_elements(By.CSS_SELECTOR, 'div > strong, .row')
    text = ''
    for row in rows:
        if len(row.find_elements(By.CSS_SELECTOR, '*')) > 3:
            continue
        text += row.text.replace('\n', ';')

    return family


def get_family_data(iin: str) -> Family | None:
    base_url, username, password = get_env_vars()
    user = User(username=username, password=password)
    auth_data = get_token(user=user, base_url=base_url)

    options = Options()
    options.add_argument('--start-maximized')
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
        driver.get(url=base_url)
        set_local_storage(driver, auth_data)
        driver.get(f'http://10.61.164.228/#/family/{iin}')
        family = get_family(driver=driver)
    return family


def convert_value(val: str) -> Any:
    if next((True for c in val if c.isalpha()), False):
        return val
    val = val.replace(' ', '')
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val


if __name__ == '__main__':
    # get_family_data(iin='880415400619')
    text = '''Общие сведения
Кол-во человек:;5
Кол-во детей:;3
Уровень семьи:;E
Адрес:;АСТАНА, ЕСИЛЬСКИЙ РАЙОН, 8
Доход за квартал
Зарплата:;0
Социальные выплаты:;120 840
Среднедушевой доход:;8 056
Совокупный доход для АСП:;212 102.87
Среднедушевой доход АСП:;14 140.19
Доход:;СДД выше нуля но ниже ЧБ
Рекомендации
АСП
Образование
Медицина
Активы семьи
Земельный участок;1
Транспорт;1
Получатели социальных выплат;1
Риски
Уровень дохода ниже ЧБ
Член семьи не имеет прикрепление к медицинской организации
Член семьи не имеет обязательное социальное медицинское страхование
Дети не посещают дошкольные организации
Социальные статусы (кол-во человек)
Дети до 18 лет;3'''

    lines = text.split('\n')
    headers = ['Общие сведения', 'Доход за квартал', 'Рекомендации', 'Активы семьи', 'Риски',
               'Социальные статусы (кол-во человек)']
    my_dict = {}

    indices = [i for i, line in enumerate(lines) if line in headers]
    print(indices)

    indices = [0, 5, 12, 16, 20, 25]
    for index, pos in enumerate(indices[:-1]):
        if ';' in lines[pos + 1]:
            my_dict[lines[pos]] = {line.split(';')[0]: convert_value(line.split(';')[1]) for line in
                                   lines[pos + 1: indices[index + 1]]}
        else:
            my_dict[lines[pos]] = lines[pos + 1: indices[index + 1]]
    rich.print(my_dict)
