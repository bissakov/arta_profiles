import json
import time
from dataclasses import dataclass
from typing import Dict, Any, List

import bs4
import httpx
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

try:
    from family_browser.utils import get_headers, is_valid_iin, get_env_vars, convert_value, timer
    from family_browser.custom_exceptions import FamilyNotFound, FamilyNotInList, WrongPassword, WrongIIN
except (ModuleNotFoundError, ImportError):
    from utils import get_headers, is_valid_iin, get_env_vars, convert_value
    from custom_exceptions import FamilyNotFound, FamilyNotInList, WrongPassword, WrongIIN


@dataclass
class User:
    username: str
    password: str


@timer
def get_token(user: User, base_url: str, client: httpx.Client) -> Dict[Any, Any]:
    response = client.post(
        url=f'{base_url}/auth/login',
        json={'username': user.username, 'password': user.password},
        timeout=3
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


# TODO page type
async def async_set_local_storage(page, storage: Dict) -> None:
    access_token = storage['accessToken']
    refresh_token = storage['refreshToken']
    user_auth = json.dumps(storage['user'], ensure_ascii=False)
    script = f"localStorage.setItem('accessToken', '{access_token}');"
    script += f"localStorage.setItem('refreshToken', '{refresh_token}');"
    script += f"localStorage.setItem('userAuth', '{user_auth}');"
    await page.evaluate(script)


def sync_set_local_storage(page, storage: Dict) -> None:
    access_token = storage['accessToken']
    refresh_token = storage['refreshToken']
    user_auth = json.dumps(storage['user'], ensure_ascii=False)
    script = f"localStorage.setItem('accessToken', '{access_token}');"
    script += f"localStorage.setItem('refreshToken', '{refresh_token}');"
    script += f"localStorage.setItem('userAuth', '{user_auth}');"
    page.evaluate(script)


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


async def async_get_family_data(iin: str) -> Any:
    if not is_valid_iin(iin=iin):
        raise WrongIIN(iin=iin)

    base_url, username, password = get_env_vars()
    user = User(username=username, password=password)
    with httpx.Client(headers=get_headers(), timeout=None) as client:
        auth_data = get_token(user=user, base_url=base_url, client=client)
        member_data = get_member_data(iin=iin, base_url=base_url, token=auth_data['accessToken'], client=client)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()
        await page.goto(base_url)
        await async_set_local_storage(page=page, storage=auth_data)
        await page.goto(f'{base_url}/#/family/{iin}')
        await page.reload()
        await page.wait_for_selector('c-col.col-md-9')

        container = await page.query_selector('c-col.col-md-9')

        soup = bs4.BeautifulSoup(
            markup=await container.inner_html(),
            features='html.parser',
        )

    general_info = get_general_info(soup=soup)
    return {'Члены семьи': member_data, **general_info}


def sync_get_family_data(iin):
    if not is_valid_iin(iin=iin):
        raise WrongIIN(iin=iin)

    base_url, username, password = get_env_vars()
    user = User(username=username, password=password)
    with httpx.Client(headers=get_headers(), timeout=None) as client:
        auth_data = get_token(user=user, base_url=base_url, client=client)
        member_data = get_member_data(iin=iin, base_url=base_url, token=auth_data['accessToken'], client=client)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        page = browser.new_page()
        page.goto(base_url)
        sync_set_local_storage(page=page, storage=auth_data)
        page.goto(f'{base_url}/#/family/{iin}')
        page.reload()
        page.wait_for_selector('c-col.col-md-9')

        soup = bs4.BeautifulSoup(
            markup=page.query_selector('c-col.col-md-9').inner_html(),
            features='html.parser',
        )

    general_info = get_general_info(soup=soup)
    return {'Члены семьи': member_data, **general_info}


if __name__ == '__main__':
    # data = get_family_data(iin='880415400619')

    start_time = time.perf_counter()
    try:
        data = sync_get_family_data(iin='880415400619')
    except httpx.ConnectTimeout:
        print('No VPN')
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.4f} seconds')

    # start_time = time.perf_counter()
    # try:
    #     data = asyncio.get_event_loop().run_until_complete(async_get_family_data(iin='880415400619'))
    # except httpx.ConnectTimeout:
    #     print('No VPN')
    # end_time = time.perf_counter()
    # elapsed_time = end_time - start_time
    # print(f'Elapsed time: {elapsed_time:.4f} seconds')

    # rich.print(data)
