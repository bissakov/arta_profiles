import json
import time
from dataclasses import dataclass
from typing import Dict, Any, List

import bs4
import httpx
import rich

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

try:
    from family_selenium.utils import get_headers, is_valid_iin, get_env_vars, convert_value, timer, async_timer
    from family_selenium.custom_exceptions import FamilyNotFound, FamilyNotInList, WrongPassword, WrongIIN
except (ModuleNotFoundError, ImportError):
    from utils import get_headers, is_valid_iin, get_env_vars, convert_value
    from family_selenium.custom_exceptions import FamilyNotFound, FamilyNotInList, WrongPassword, WrongIIN


@dataclass
class User:
    username: str
    password: str


@timer
def get_token(user: User, base_url: str, client: httpx.Client) -> Dict[Any, Any]:
    response = client.post(
        url=f'{base_url}/auth/login',
        json={'username': user.username, 'password': user.password},
    )
    response.raise_for_status()
    return response.json()


@timer
def get_member_data(iin: str, base_url: str, token: str, client: httpx.Client) -> List[Dict[str, str]]:
    client.headers['Authorization'] = f'Bearer {token}'
    response = client.post(url=f'{base_url}/api/card/familyInfo', json={'iin': iin})
    response.raise_for_status()
    family_data = response.json()

    if family_data['family'] is None:
        raise FamilyNotFound(iin=iin)

    member_data = [{'ИИН': member['iin'], 'ФИО': member['fullName']} for member in family_data['familyMemberList']]
    selected_member_info = next((i, member) for i, member in enumerate(member_data) if member['ИИН'] == iin)
    member_data.pop(selected_member_info[0])
    member_data.insert(0, selected_member_info[1])
    return member_data


@timer
def set_local_storage(driver: WebDriver, storage: Dict) -> None:
    access_token = storage['accessToken']
    refresh_token = storage['refreshToken']
    user_auth = json.dumps(storage['user'], ensure_ascii=False)
    script = f"localStorage.setItem('accessToken', '{access_token}');"
    script += f"localStorage.setItem('refreshToken', '{refresh_token}');"
    script += f"localStorage.setItem('userAuth', '{user_auth}');"
    driver.execute_script(script)


@timer
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


@timer
def get_family_data(iin: str, driver: WebDriver = None) -> Any:
    if not is_valid_iin(iin=iin):
        raise WrongIIN(iin=iin)

    base_url, username, password = get_env_vars()
    user = User(username=username, password=password)
    with httpx.Client(headers=get_headers(), timeout=None) as client:
        auth_data = get_token(user=user, base_url=base_url, client=client)
        member_data = get_member_data(iin=iin, base_url=base_url, token=auth_data['accessToken'], client=client)

    if not driver:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    with driver:
        driver.get(url=base_url)
        set_local_storage(driver, auth_data)
        driver.get(f'{base_url}/#/family/{iin}')
        driver.implicitly_wait(10)
        soup = bs4.BeautifulSoup(
            # markup=driver.find_element(By.CLASS_NAME, 'col-md-9').get_attribute('innerHTML'),
            markup=driver.page_source,
            features='html.parser',
            parse_only=bs4.SoupStrainer('div', attrs={'class': 'col-md-9'})
        )

    general_info = get_general_info(soup=soup)
    return {'Члены семьи': member_data, **general_info}


async def puppeteer_get_family_data(iin: str) -> Any:
    base_url, username, password = get_env_vars()
    user = User(username=username, password=password)
    with httpx.Client(headers=get_headers(), timeout=None) as client:
        auth_data = get_token(user=user, base_url=base_url, client=client)
        member_data = get_member_data(iin=iin, base_url=base_url, token=auth_data['accessToken'], client=client)

    browser = await launch(headless=False, defaultViewport=None, args=['--start-maximized'])
    page = await browser.newPage()
    await page.goto(base_url)
    access_token = auth_data['accessToken']
    refresh_token = auth_data['refreshToken']
    user_auth = json.dumps(auth_data['user'], ensure_ascii=False)
    script = f"localStorage.setItem('accessToken', '{access_token}');"
    script += f"localStorage.setItem('refreshToken', '{refresh_token}');"
    script += f"localStorage.setItem('userAuth', '{user_auth}');"
    await page.evaluate(script)
    await page.goto(f'{base_url}/#/family/{iin}', waitUntil='networkidle2')
    await page.waitForSelector('div.col-md-9')

    soup = bs4.BeautifulSoup(
        markup=await page.evaluate('document.querySelector("div.col-md-9").innerHTML'),
        features='html.parser',
        parse_only=bs4.SoupStrainer('div', attrs={'class': 'col-md-9'})
    )

    await browser.close()

    general_info = get_general_info(soup=soup)
    return {'Члены семьи': member_data, **general_info}


if __name__ == '__main__':
    # data = get_family_data(iin='880415400619')

    import asyncio
    from pyppeteer import launch

    start_time = time.perf_counter()

    data = asyncio.get_event_loop().run_until_complete((puppeteer_get_family_data(iin='880415400619')))

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.4f} seconds')

    rich.print(data)
