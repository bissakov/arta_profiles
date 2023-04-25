from dataclasses import dataclass, field, fields, asdict
from typing import List, Dict

try:
    from family.utils import get_social_status_dict
except (ModuleNotFoundError, ImportError):
    from utils import get_social_status_dict


@dataclass
class User:
    username: str
    password: str


@dataclass
class Member:
    iin: str
    full_name: str

    def __post_init__(self):
        self.full_name = ' '.join([name.capitalize() for name in self.full_name.split(' ')])

    def to_dict(self) -> Dict[str, str]:
        return {'ИИН': self.iin, 'ФИО': self.full_name} 


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
    need_asp: bool = False
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
    nedv_cnt: int = 0
    transport_cnt: int = 0


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
            'Члены семьи': [member.to_dict() for member in self.members],
            'Общие сведения': {
                'Кол-во человек': self.member_cnt,
                'Кол-во детей': self.child_cnt,
                'Уровень семьи': self.family_level,
                'Адрес': self.address
                },
            'Доход за квартал': {
                'Зарплата': self.salary,
                'Социальные выплаты': self.social_payment,
                'Среднедушевой доход': self.per_capita_income,
                'Совокупный доход для АСП': self.total_income_asp,
                'Среднедушевой доход АСП': self.per_capita_income_asp,
                'Доход': self.income
                },
            'Рекомендации': self.recommendations.to_dict(),
            'Активы семьи': {
                'Земельный участок': self.assets.land_cnt,
                'Кол-во трудоустроенных членов семьи': self.assets.emp_cnt,
                'Получатели социальных выплат': self.assets.soc_pay_recipient_cnt,
                'Жилая недвижимось': self.assets.nedv_cnt,
                'Транспорт': self.assets.transport_cnt
                },
            'Риски': self.risks.to_dict(),
            'Социальные статусы (кол-во человек)': {key: value for key, value in self.social_status.items() if value > 0},
        }
