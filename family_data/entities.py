from dataclasses import dataclass, field, fields
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

    def to_dict(self):
        return {risk.name: getattr(self, risk.name)
                for risk in fields(self)
                if getattr(self, risk.name)}


@dataclass
class Recommendations:
    need_asp: bool = True
    need_edu: bool = False
    need_med: bool = False
    need_emp: bool = False
    need_nedv: bool = False

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
    land_cnt: int = 0
    emp_cnt: int = 0
    soc_pay_recipient_cnt: int = 0
    risks: Risks = Risks()
    social_status: Dict[str, int] = field(default_factory=get_social_status_dict)

    def to_dict(self) -> Dict:
        return {
            'members': [member.full_name for member in self.members],
            'member_cnt': self.member_cnt,
            'child_cnt': self.child_cnt,
            'family_level': self.family_level,
            'address': self.address,
            'salary': self.salary,
            'social_payment': self.social_payment,
            'per_capita_income': self.per_capita_income,
            'total_income_asp': self.total_income_asp,
            'per_capita_income_asp': self.per_capita_income_asp,
            'income': self.income,
            'recommendations': self.recommendations.to_dict(),
            'land_cnt': self.land_cnt,
            'emp_cnt': self.emp_cnt,
            'soc_pay_recipient_cnt': self.soc_pay_recipient_cnt,
            'risks': self.risks.to_dict(),
            'social_status': {key: value for key, value in self.social_status.items() if value > 0},
        }
