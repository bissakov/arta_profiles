import json
import time
from dataclasses import dataclass
from typing import Dict, Any, List
import bs4
import httpx
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Page

try:
    from family.utils import get_headers, is_valid_iin, get_env_vars, convert_value
    from family.custom_exceptions import FamilyNotFound, WrongIIN
except (ModuleNotFoundError, ImportError):
    from utils import get_headers, is_valid_iin, get_env_vars, convert_value
    from custom_exceptions import FamilyNotFound, WrongIIN


@dataclass
class User:
    username: str
    password: str


def get_token(user: User, base_url: str, client: httpx.Client) -> Dict[Any, Any]:
    response = client.post(
        url=f'{base_url}/auth/login',
        json={'username': user.username, 'password': user.password},
        timeout=3
    )
    response.raise_for_status()
    return response.json()


def get_member_data(iin: str, base_url: str, token: str, client: httpx.Client) -> List[Dict[str, str]]:
    client.headers['Authorization'] = f'Bearer {token}'
    response = client.post(url=f'{base_url}/api/card/familyInfo', json={'iin': iin})
    response.raise_for_status()
    family_data = response.json()

    if family_data['family'] is None:
        raise FamilyNotFound(iin=iin)
 
    member_list = family_data['familyMemberList']

    member_data = []
    selected_member_info = None
    for member in member_list:
        member_info = {'ИИН': member['iin'], 'ФИО': member['fullName']}
        if member['iin'] == iin:
            selected_member_info = member_info
        else:
            member_data.append(member_info)
    member_data.insert(0, selected_member_info)
    return member_data


def set_local_storage(page: Page, storage: Dict) -> None:
    access_token = storage['accessToken']
    refresh_token = storage['refreshToken']
    user_auth = json.dumps(storage['user'], ensure_ascii=False)
    script = f"localStorage.setItem('accessToken', '{access_token}');"
    script += f"localStorage.setItem('refreshToken', '{refresh_token};');"
    script += f"localStorage.setItem('userAuth', '{user_auth}');"
    page.evaluate(script)


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


def get_family_data(iin) -> Dict[str, List | Dict]:
    if not is_valid_iin(iin=iin):
        raise WrongIIN(iin=iin)

    base_url, username, password = get_env_vars()
    user = User(username=username, password=password)
    with httpx.Client(headers=get_headers(), timeout=None) as client:
        auth_data = get_token(user=user, base_url=base_url, client=client)
        member_data = get_member_data(
            iin=iin,
            base_url=base_url,
            token=auth_data['accessToken'],
            client=client
        )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        page = browser.new_page()
        page.goto(base_url)
        set_local_storage(page=page, storage=auth_data)
        page.goto(f'{base_url}/#/family/{iin}')
        page.reload()

        container_selector = 'c-col.col-md-9'
        page.wait_for_selector(container_selector)

        container = page.query_selector(container_selector)

        if not container:
            raise ValueError(f'{container_selector} not found')

        general_info = get_general_info(
            soup=bs4.BeautifulSoup(
                markup=container.inner_html(),
                features='html.parser'
            )
        )

    return {'Члены семьи': member_data, **general_info}


if __name__ == '__main__':
    import rich

    data = None
    start_time = time.perf_counter()
    try:
        data = get_family_data(iin='880415400619')
    except httpx.ConnectTimeout:
        print('No VPN')
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.4f} seconds')

    rich.print(data)

