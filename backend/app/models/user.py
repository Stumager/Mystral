from datetime import date, datetime, time
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: Optional[str] = Field(default=None, index=True)
    display_name: Optional[str] = None
    lang: str = Field(default="ru")
    subscription_tier: str = Field(default="free")
    subscription_expires_at: Optional[datetime] = None
    balance_coins: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuthProvider(SQLModel, table=True):
    __tablename__ = "auth_providers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    provider: str
    provider_id: str
    password_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    birth_date: Optional[date] = None
    birth_time: Optional[time] = None
    birth_time_known: bool = Field(default=False)
    birth_city: Optional[str] = None
    birth_lat: Optional[float] = None
    birth_lng: Optional[float] = None
    birth_name_enc: Optional[str] = None
    current_name_enc: Optional[str] = None
    full_name: Optional[str] = None
    timezone: Optional[str] = None
    notifications_enabled: bool = Field(default=False)


class TarotReading(SQLModel, table=True):
    __tablename__ = "tarot_readings"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    spread_id: str
    question: Optional[str] = None
    cards_json: str = ""
    interpretation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserPartner(SQLModel, table=True):
    __tablename__ = "user_partners"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    label: str
    birth_date: date
    birth_time: Optional[time] = None
    birth_city: Optional[str] = None
    birth_lat: Optional[float] = None
    birth_lng: Optional[float] = None
    zodiac_sign: Optional[str] = None
    chinese_sign: Optional[str] = None
    life_path: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
