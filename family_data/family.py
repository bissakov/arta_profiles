import asyncio
import os
from dataclasses import asdict
from time import sleep
from typing import List, Dict
import dotenv
import httpx
import rich

try:
    from family_data.entities import User, Family, Member, Risks
    from family_data.utils import get_headers, get_risk_dict, FamilyNotFound, FamilyNotInList
except (ModuleNotFoundError, ImportError):
    from entities import User, Family, Member, Risks
    from utils import get_headers, get_risk_dict, FamilyNotFound, FamilyNotInList


def get_token(client: httpx.Client, user: User, base_url: str) -> Dict:
    url = f'{base_url}/auth/login'

    headers = get_headers()

    response = client.post(
        url=url,
        json={'username': user.username, 'password': user.password},
        headers=headers
    )
    response.raise_for_status()

    return response.json()


def get_risks(risk_detail: str) -> Risks:
    risk_dict = get_risk_dict()

    risks = Risks()
    for detail in risk_detail:
        if detail == 'N':
            continue
        risk = risk_dict[detail]
        setattr(risks, risk['key'], risk['value'])

    return risks


def get_member_data(family_data: Dict) -> List[Member]:
    return [Member(iin=member['iin'], full_name=member['fullName']) for member in family_data['familyMemberList']]


async def get_person_details(family: Family, async_client: httpx.AsyncClient, base_url: str) -> List[Dict]:
    results = []
    api_url = f'{base_url}/api/card/getPersonDetailsDTOByIin'
    if len(family.members) == 1:
        async with async_client.post(url=api_url, json={'iin': family.members[0]}) as response:
            results.append(response.json())
    else:
        tasks = [async_client.post(url=api_url, json={'iin': member.iin}) for member in family.members]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results.append(response.json())
    return results


async def update_social_status(family: Family, client: httpx.Client, base_url: str) -> None:
    async with httpx.AsyncClient(headers=client.headers, timeout=None) as async_client:
        person_details = await get_person_details(async_client=async_client, family=family, base_url=base_url)

    social_status = family.social_status
    for person_detail in person_details:
        for person_source in person_detail['personSourceList']:
            status_name = person_source['status']['nameRu']
            social_status[status_name] += 1


def get_data(client: httpx.Client, api_url: str, iin: str or int) -> Dict:
    response = client.post(url=api_url, json={'iin': iin})
    return response.json()


def family_exists(family_data: Dict) -> bool:
    return bool(family_data['family'])


def is_family_in_list(client: httpx.Client, base_url: str, iin: str) -> bool:
    url = f'{base_url}/api/workspace/stat/page'

    payload = {
        'regionId': None,
        'actionCode': '',
        'countId': 93,
        'iin': iin,
        'page': 1,
        'size': 1
    }

    response = client.post(url=url, json=payload)

    return response.json()['total'] > 0


def get_family(client: httpx.Client, base_url: str, iin: int or str) -> Family:
    family_data = get_data(client=client, api_url=f'{base_url}/api/card/familyInfo', iin=iin)

    if not family_exists(family_data=family_data):
        raise FamilyNotFound(iin=iin)
    if not is_family_in_list(client=client, base_url=base_url, iin=iin):
        raise FamilyNotInList(iin=iin)

    family = Family()

    family.members = get_member_data(family_data=family_data)
    asyncio.run(update_social_status(family=family, client=client, base_url=base_url))

    family_quality = family_data['family']['familyQuality']

    family.member_cnt = family_quality['cntMem']
    family.child_cnt = family_quality['cntChild']
    family.family_level = family_quality['tzhsDictionary']['nameRu']
    family.address = family_data['addressRu']

    family.salary = family_quality['incomeOop']
    family.social_payment = family_quality['incomeCbd']
    family.per_capita_income = family_quality['sdd']
    family.per_capita_income_asp = family_quality['sddAsp']
    family.total_income_asp = family.per_capita_income_asp * family.member_cnt * 3
    family.income = family_quality['familyPm']['nameRu']

    family.recommendations.need_edu = bool(family_quality['needEdu'])
    family.recommendations.need_emp = bool(family_quality['needEmp'])
    family.recommendations.need_med = bool(family_quality['needMed'])
    family.recommendations.need_nedv = bool(family_quality['needNedv'])

    family.assets.land_cnt = family_quality['cntLand']
    family.assets.emp_cnt = family_quality['cntEmp']
    family.assets.soc_pay_recipient_cnt = family_quality['cntCbd']
    risk_detail = family_quality['riskDetail']
    family.risks = get_risks(risk_detail=risk_detail)

    return family


def get_family_data(iin: str or int) -> Family or None:
    dotenv.load_dotenv()
    user = User(username=os.getenv('USR'), password=os.getenv('PSW'))
    base_url = os.getenv('URL')

    with httpx.Client(timeout=None) as client:
        auth_data = get_token(user=user, client=client, base_url=base_url)
        user.token = auth_data['accessToken']
        user.user_id = str(auth_data['user']['userId'])

        client.headers = get_headers()
        client.headers['Authorization'] = f'Bearer {user.token}'

        family = get_family(client=client, base_url=base_url, iin=iin)

    return family


if __name__ == '__main__':
    data: Family = get_family_data(iin=5416132165)

    print(data)

    pass