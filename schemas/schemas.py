"""
Data models and validation schemas for the lead generation system
"""
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SearchCriteria:
    size_range: str
    industry: str
    location: Optional[str] = None

@dataclass
class Company:
    name: str
    website: Optional[str] = None
    employee_count: Optional[int] = None
    industry: Optional[str] = None
    location: Optional[str] = None

@dataclass
class Lead:
    company: Company
    insights: dict
    personalized_message: str
    contacts: List[dict] = None  # Hunter.io contact information 