import os
from typing import Dict
import httpx
from dotenv import load_dotenv
from entities import User, Family, Member, Risks, SocialStatus
from utils import get_headers


def get_risks(risk_detail: str) -> Risks:
    risk_dict = {
        'I': {'key': 'income', 'value': 'Уровень дохода ниже ЧБ'},
        'C': {'key': 'credit', 'value': 'Семья имеет задолженность по кредиту больше 90 дней'},
        'M': {'key': 'medical_attachment', 'value': 'Член семьи не имеет прикрепление к медицинской организации'},
        'D': {'key': 'dispensary', 'value': 'Член семьи состоит на диспансерном учете'},
        'O': {'key': 'health_insurance', 'value': 'Член семьи не имеет прикрепление к медицинской организации'},
        'S': {'key': 'preschool', 'value': 'Дети не посещают дошкольные организации'},
        'E': {'key': 'school', 'value': 'Дети не посещают школы'}
    }

    risks = Risks()
    for detail in risk_detail:
        if detail == 'N':
            continue
        risk = risk_dict.get(detail)
        setattr(risks, risk.get('key'), risk.get('value'))

    return risks


def get_member_data(family_data: Dict):
    return [Member(iin=member['iin'], full_name=member['fullName']) for member in family_data['familyMemberList']]


def get_social_status(family: Family, client: httpx.Client, base_url: str):
    social_status = SocialStatus()
    for member in family.members:
        member_iin = member.iin
        person_data = get_data(client=client, api_url=f'{base_url}/api/card/getPersonDetailsDTOByIin', iin=member_iin)
        for person_detail in person_data['personSourceList']:
            status_name = person_detail['status']['nameRu']
            if status_name in social_status.get_names():
                social_status.update(status_name=status_name)
    return social_status


def get_data(client: httpx.Client, api_url: str, iin: str or int):
    response = client.post(url=api_url, json={'iin': iin})
    return response.json()


def parse(base_url: str, iin: int, token: str):
    family = Family()

    headers = get_headers()
    headers['Authorization'] = f'Bearer {token}'
    headers['Content-Type'] = 'application/json'
    with httpx.Client(headers=headers, timeout=None) as client:
        family_data = get_data(client=client, api_url=f'{base_url}/api/card/familyInfo', iin=iin)
        family.members = get_member_data(family_data=family_data)

        family.social_status = get_social_status(family=family, client=client, base_url=base_url)

    # ✅✅✅ Кол-во человек: numericinput_number_of_family ✅✅✅
    member_count = family_data.get('family').get('familyQuality').get('cntMem')

    # ✅✅✅ Кол-во детей: numericinput_number_of_child ✅✅✅
    child_count = family_data.get('family').get('familyQuality').get('cntChild')

    # ✅✅✅ Уровень семьи: textbox_level_fam ✅✅✅
    family_level = family_data.get('family').get('familyQuality').get('tzhsDictionary').get('nameRu')

    # ✅✅✅ Адрес: textbox_address ✅✅✅
    address = family_data.get('addressRu')

    # ❓❓❓ Зарплата: numericinput_salary TODO
    salary = family_data.get('family').get('familyQuality').get('incomeOop')

    # ❓❓❓ Социальные выплаты: numericinput_cots_vyplaty TODO
    social_payment = family_data.get('family').get('familyQuality').get('incomeCbd')

    # ❓❓❓ Среднедушевой доход: numericinput_cots_income TODO
    per_capita_income = family_data.get('family').get('familyQuality').get('sdd')

    # ❓❓❓ Среднедушевой доход для АСП: numericinput_mid_income_ASP TODO
    per_capita_income_asp = family_data.get('family').get('familyQuality').get('sddAsp')

    # ❓❓❓ Совокупный доход для АСП: numericinput_income_ASP TODO
    total_income_asp = per_capita_income_asp * member_count * 3

    # ❓❓❓ Доход: textbox_income TODO
    income = family_data.get('family').get('familyQuality').get('familyPm').get('nameRu')

    # Рекомендации: check_rec
    need_edu = family_data.get('family').get('familyQuality').get('needEdu')
    need_emp = family_data.get('family').get('familyQuality').get('needEmp')
    need_med = family_data.get('family').get('familyQuality').get('needMed')
    need_nedv = family_data.get('family').get('familyQuality').get('needNedv')
    need_asp = 1

    # ✅✅✅ Жилая недвижимость: textbox_count_home ✅✅✅
    land_number = family_data.get('family').get('familyQuality').get('cntLand')

    # ✅✅✅ Кол-во трудоустроенных членов семьи: textbox_worker_fam ✅✅✅
    emp_number = family_data.get('family').get('familyQuality').get('cntEmp')

    # Получатели социальных выплат: textbox_count_cots_income
    soc_pay_recipient_count = family_data.get('family').get('familyQuality').get('cntCbd')

    # Риски: textbox_risks
    risk_detail = family_data.get('family').get('familyQuality').get('riskDetail')
    risks = get_risks(risk_detail=risk_detail)

    # Член многодетной семьи: numericinput_have_many_ch

    # Дети до 18 лет: numericinput_ch_eightn

    # Наемные работники: numericinput_naemniki

    # Многодетные семьи: numericinput_count_ch_large

    # Получатель пособий: numericinput_akimat_give



if __name__ == '__main__':
    load_dotenv()

    _user = User(username=os.getenv('USR'), password=os.getenv('PSW'))
    _base_url = os.getenv('URL')
    parse(base_url=_base_url, iin=861220450614, token='eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJVU0VSMjE3IiwiaWF0IjoxNjgwODU2NTgyLCJleHAiOjE2ODA4NTgzODJ9.HPGuRa9mJJwIoHTHHrpvBJPoP2Tzj17TZ2s4A11ydZGMRFYTHXF-zhwkaMCpMWJyaU-Gzj-LlDjirpxqizbzfg')

    # print(get_risks(riskDetail='INNNOSN'))

