import asyncio
import json
import time
from typing import Any, Dict, List

import httpx

try:
    from family.custom_exceptions import FamilyNotFound, WrongIIN
    from family.utils import get_env_vars, get_headers, is_valid_iin, get_risk_dict
    from family.entities import User, Family, Member, Risks
except (ModuleNotFoundError, ImportError):
    from custom_exceptions import FamilyNotFound, WrongIIN
    from utils import get_env_vars, get_headers, is_valid_iin, get_risk_dict
    from entities import User, Family, Member, Risks


def get_token(user: User, base_url: str, client: httpx.Client) -> Dict[Any, Any]:
    response = client.post(
        url=f'{base_url}/auth/login',
        json={'username': user.username, 'password': user.password},
        timeout=3
    )
    response.raise_for_status()
    return response.json()


def get_data(client: httpx.Client, api_url: str, iin: str) -> Dict:
    response = client.post(url=api_url, json={'iin': iin})
    return response.json()


def get_member_data(family_data: Dict, iin: str) -> List[Member]:
    member_list = family_data['familyMemberList']

    members = []
    selected_member = None
    for member in member_list:
        member = Member(iin=member['iin'], full_name=member['fullName'])
        if member.iin == iin:
            selected_member = member
        else:
            members.append(member)
    members.insert(0, selected_member)
    return members


def family_exists(family_data: Dict) -> bool:
    return bool(family_data['family'])


async def get_person_details(family: Family, async_client: httpx.AsyncClient, base_url: str) -> List[Dict]:
    results = []
    api_url = f'{base_url}/api/card/getPersonDetailsDTOByIin'
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


def get_risks(risk_detail: str) -> Risks:
    risk_dict = get_risk_dict()
    risks = Risks()
    for detail in risk_detail:
        if detail == 'N':
            continue
        risk = risk_dict[detail]
        setattr(risks, risk['key'], risk['value'])
    return risks


def get_value(val) -> int:
    return val if val is not None else 0


def get_family(client: httpx.Client, base_url: str, iin: str) -> Family:
    family_data = get_data(client=client, api_url=f'{base_url}/api/card/familyInfo', iin=iin)

    if not family_exists(family_data=family_data):
        raise FamilyNotFound()

    family = Family()

    family.members = get_member_data(family_data=family_data, iin=iin)
    asyncio.run(update_social_status(family=family, client=client, base_url=base_url))
    
    family_quality = family_data['family']['familyQuality']

    family.member_cnt = family_quality['cntMem']
    family.child_cnt = family_quality['cntChild']
    family.family_level = family_quality['tzhsDictionary']['nameRu']
    family.address = family_data['addressRu']

    family.salary = get_value(family_quality['incomeOop'])
    family.social_payment = get_value(family_quality['incomeCbd'])
    family.per_capita_income = get_value(family_quality['sdd'])
    family.per_capita_income_asp = get_value(family_quality['sddAsp'])
    family.total_income_asp = family.per_capita_income_asp * family.member_cnt * 3
    family.income = family_quality['familyPm']['nameRu']

    family.recommendations.need_asp = family.per_capita_income_asp != None and family.per_capita_income_asp >= 0
    family.recommendations.need_edu = bool(family_quality['needEdu'])
    family.recommendations.need_emp = bool(family_quality['needEmp'])
    family.recommendations.need_med = bool(family_quality['needMed'])
    family.recommendations.need_nedv = bool(family_quality['needNedv'])

    family.assets.land_cnt = family_quality['cntLand']
    family.assets.emp_cnt = family_quality['cntEmp']
    family.assets.soc_pay_recipient_cnt = family_quality['cntCbd']
    family.assets.nedv_cnt = family_quality['cntNedv']
    family.assets.transport_cnt = family_quality['cntDv']

    risk_detail = family_quality['riskDetail']
    family.risks = get_risks(risk_detail=risk_detail)
    
    return family


def get_family_data(iin: str or None) -> Dict: 
    if iin is None or not is_valid_iin(iin=iin):
        raise WrongIIN()

    base_url, username, password = get_env_vars()
    user = User(username=username, password=password)
    with httpx.Client(headers=get_headers(), timeout=None) as client:
        auth_data = get_token(user=user, base_url=base_url, client=client)
        token = auth_data['accessToken']
        client.headers['Authorization'] = f'Bearer {token}'
        family = get_family(client=client, base_url=base_url, iin=iin)

    return family.to_dict()


if __name__ == '__main__':
    import json

    import rich

    data = None
    start_time = time.perf_counter()
    try:
        data = get_family_data(iin=iin)
    except httpx.ConnectTimeout:
        print('No VPN')
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.4f} seconds')

    # with open('test.json', 'w') as f:
        # json.dump(data, f, ensure_ascii=False, indent=4)

    rich.print(data)

