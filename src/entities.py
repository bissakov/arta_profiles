from dataclasses import dataclass, fields
from typing import List


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


@dataclass
class Risks:
    income: str = None
    credit: str = None
    medical_attachment: str = None
    dispensary: str = None
    health_insurance: str = None
    preschool: str = None
    school: str = None


@dataclass
class SocialStatus:
    member_of_a_large_family_cnt: int = 0
    children_under_18_cnt: int = 0
    wage_earner_cnt: int = 0
    large_families_cnt: int = 0
    beneficiary_cnt: int = 0

    @staticmethod
    def get_names():
        return ['Член многодетной семьи ', 'Дети до 18 лет', 'Наемные работники', 'Многодетные семьи', 'Получатель пособий']

    def get_mappings(self):
        return {field.name: name for field, name in zip(fields(self), self.get_names())}

    def update(self, status_name):
        mapping = self.get_mappings()
        for key, value in mapping.items():
            if value == status_name:
                setattr(self, key, getattr(self, key) + 1)


@dataclass()
class Recommendations:
    need_asp: bool = True
    need_edu: bool = False
    need_med: bool = False
    need_emp: bool = False
    need_nedv: bool = False


@dataclass
class Family:
    members: List[Member] = None
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
    land_cnt: int = 0
    emp_cnt: int = 0
    soc_pay_recipient_cnt: int = 0
    risks: Risks = Risks()
    social_status: SocialStatus = SocialStatus()

    def __post_init__(self):
        self.members = []
