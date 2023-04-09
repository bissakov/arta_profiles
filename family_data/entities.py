from dataclasses import dataclass, fields, field
from typing import List, Dict
from family_data.utils import get_social_status_dict


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
    social_status: Dict[str, int] = field(default_factory=get_social_status_dict)

    def __post_init__(self):
        self.members = []
