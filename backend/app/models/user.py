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
    email_verified: bool = Field(default=False)
    verification_code: Optional[str] = None
    verification_code_expires_at: Optional[datetime] = None
    reset_token: Optional[str] = None
    reset_token_expires_at: Optional[datetime] = None
    pending_email: Optional[str] = None
    pending_email_code: Optional[str] = None
    pending_email_expires_at: Optional[datetime] = None
    ref_code: Optional[str] = Field(default=None, index=True)
    referred_by: Optional[UUID] = None
    ref_bonus_days_given: int = Field(default=0)
    is_active: bool = Field(default=True)
    deletion_scheduled_at: Optional[datetime] = None
    subscription_created_at: Optional[datetime] = None
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
    push_subscription: Optional[str] = None  # JSON string of PushSubscription


class TarotReading(SQLModel, table=True):
    __tablename__ = "tarot_readings"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    spread_id: str
    question: Optional[str] = None
    cards_json: str = ""
    interpretation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RuneReading(SQLModel, table=True):
    __tablename__ = "rune_readings"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    spread_type: str
    question: Optional[str] = None
    runes_json: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReadingInterpretation(SQLModel, table=True):
    """TZ-092: caches a generated AI interpretation to the (reading_id, lang)
    that produced it — same compound-key pattern as SeoContent's
    (page_type, slug, lang) — so a persisted tarot/rune reading (TZ-092/
    QA-003's day/year read-back) doesn't re-bill OpenRouter and doesn't
    show different wording on every re-view of the same reading."""
    __tablename__ = "reading_interpretations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    reading_id: UUID = Field(index=True)
    reading_type: str  # "tarot" | "rune" — reading_id alone is already
    # collision-free (independent UUID4 spaces), this is for clear,
    # indexable querying/debugging, not disambiguation.
    lang: str = Field(default="ru")
    text: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReferralLog(SQLModel, table=True):
    __tablename__ = "referral_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    referrer_id: UUID = Field(foreign_key="users.id")
    referred_id: UUID = Field(foreign_key="users.id")
    bonus_days: int = Field(default=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = None
    section: Optional[str] = None
    is_published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SeoContent(SQLModel, table=True):
    __tablename__ = "seo_content"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    page_type: str = Field(index=True)
    slug: str = Field(index=True)
    lang: str = Field(default="ru")
    content: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)


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


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    provider: str = Field(default="yukassa")
    provider_payment_id: str = Field(index=True, unique=True)
    product: str
    amount: str
    currency: str = Field(default="RUB")
    status: str = Field(default="pending")  # pending | succeeded | canceled | refunded
    metadata_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RefundRequest(SQLModel, table=True):
    __tablename__ = "refund_requests"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    payment_id: UUID = Field(foreign_key="payments.id", index=True)
    status: str = Field(default="pending")  # pending | rejected | completed | failed
    reason: Optional[str] = None
    admin_comment: Optional[str] = None
    error_detail: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
