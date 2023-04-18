from dataclasses import dataclass, field, fields, asdict
from typing import List, Dict

try:
    from family_data.utils import get_social_status_dict
except (ModuleNotFoundError, ImportError):
    from utils import get_social_status_dict


@dataclass
class User:
    username: str
    password: str
    token: str = None
    user_id: str = None


@dataclass
class Member:
    iin: str
    full_name: str

    def __post_init__(self):
        self.full_name = ' '.join([name.capitalize() for name in self.full_name.split(' ')])


@dataclass
class Risks:
    income: str = None
    credit: str = None
    medical_attachment: str = None
    dispensary: str = None
    health_insurance: str = None
    preschool: str = None
    school: str = None

    def to_dict(self):
        names = [
            'Уровень дохода ниже ЧБ',
            'Семья имеет задолженность по кредиту больше 90 дней',
            'Член семьи не имеет прикрепление к медицинской организации',
            'Член семьи состоит на диспансерном учете',
            'Член семьи не имеет обязательное социальное медицинское страхование',
            'Дети не посещают дошкольные организации',
            'Дети не посещают школы'
        ]
        return [name for risk, name in zip(fields(self), names) if getattr(self, risk.name)]


@dataclass
class Recommendations:
    need_asp: bool = True
    need_edu: bool = False
    need_med: bool = False
    need_emp: bool = False
    need_nedv: bool = False

    def to_dict(self) -> List[str]:
        names = ['АСП', 'Образование', 'Медицина', 'Трудоустройство', 'Жилье']
        return [name for recommendation, name in zip(fields(self), names) if getattr(self, recommendation.name)]


@dataclass
class Assets:
    land_cnt: int = 0
    emp_cnt: int = 0
    soc_pay_recipient_cnt: int = 0

    def to_dict(self) -> Dict[str, bool]:
        return {recommendation.name: getattr(self, recommendation.name)
                for recommendation in fields(self)
                if getattr(self, recommendation.name)}


@dataclass
class Family:
    members: List[Member] = field(default_factory=list)
    member_cnt: int = 0
    child_cnt: int = 0
    family_level: str = None
    address: str = None
    salary: int = 0
    social_payment: int = 0
    per_capita_income: int = 0
    total_income_asp: int = 0
    per_capita_income_asp: int = 0
    income: str = None
    recommendations: Recommendations = Recommendations()
    assets: Assets = Assets()
    risks: Risks = Risks()
    social_status: Dict[str, int] = field(default_factory=get_social_status_dict)

    def to_dict(self) -> Dict:
        return {
            'members': [asdict(member) for member in self.members],
            'member_cnt': {'name': 'Кол-во человек', 'value': self.member_cnt},
            'child_cnt': {'name': 'Кол-во детей', 'value': self.child_cnt},
            'family_level': {'name': 'Уровень семьи', 'value': self.family_level},
            'address': {'name': 'Адрес', 'value': self.address},
            'salary': {'name': 'Зарплата', 'value': self.salary},
            'social_payment': {'name': 'Социальные выплаты', 'value': self.social_payment},
            'per_capita_income': {'name': 'Среднедушевой доход', 'value': self.per_capita_income},
            'total_income_asp': {'name': 'Совокупный доход для АСП', 'value': self.total_income_asp},
            'per_capita_income_asp': {'name': 'Среднедушевой доход АСП', 'value': self.per_capita_income_asp},
            'income': {'name': 'Доход', 'value': self.income},
            'recommendations': self.recommendations.to_dict(),
            'land_cnt': {'name': 'Жилая недвижимость', 'value': self.assets.land_cnt},
            'emp_cnt': {'name': 'Кол-во трудоустроенных членов семьи', 'value': self.assets.emp_cnt},
            'soc_pay_recipient_cnt': {'name': 'Получатели социальных выплат', 'value': self.assets.soc_pay_recipient_cnt},
            'risks': self.risks.to_dict(),
            'social_status': {key: value for key, value in self.social_status.items() if value > 0},
        }