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


@dataclass
class Family:
    members: List[Member] = None
    member_count: int = None
    child_count: int = None
    family_level: str = None
    address: str = None
    salary: int = None
    social_payment: int = None
    pc_income: int = None
    total_income: int = None
    income: str = None
    land_number: int = None
    emp_number: int = None
    social_status: SocialStatus = SocialStatus()

    def __post_init__(self):
        self.members = []
