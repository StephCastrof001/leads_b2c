from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Platform(str, Enum):
    IG_KEYWORD = "ig_keyword"
    FB_KEYWORD = "fb_keyword"
    TIKTOK_KEYWORD = "tiktok_keyword"
    GOOGLE_MAPS = "google_maps"
    IG_FOLLOWERS = "ig_followers"


class ScrapeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Lead:
    platform: Platform
    keyword: str
    email: str
    name: str
    link: str
    phone: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScrapeJob:
    id: str
    platform: Platform
    keyword: str
    status: ScrapeStatus = ScrapeStatus.PENDING
    credits_used: int = 0
    leads: List[Lead] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class ScrapeResult:
    jobs: List[ScrapeJob] = field(default_factory=list)
    total_credits_used: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    total_leads: int = 0
    success_rate: float = 0.0
