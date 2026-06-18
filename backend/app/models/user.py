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
    balance_coins: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuthProvider(SQLModel, table=True):
    __tablename__ = "auth_providers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    provider: str
    provider_id: str
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
    timezone: Optional[str] = None


class UserPartner(SQLModel, table=True):
    __tablename__ = "user_partners"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    label: str
    birth_date: date
    birth_time: Optional[time] = None
    birth_city: Optional[str] = None
