from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

# --- Admin Schemas ---
class AdminLogin(BaseModel):
    username: EmailStr
    password: str = Field(min_length=1, max_length=1024)

    @field_validator("username")
    @classmethod
    def require_cyberpro_address(cls, value: str) -> str:
        address = str(value).strip().lower()
        if not address.endswith("@cyberpro.ke"):
            raise ValueError("Use your @cyberpro.ke administrator email")
        return address

class Token(BaseModel):
    access_token: str
    token_type: str

class AdminUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str

# --- Program Schemas ---
class ProgramBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    desc: str = Field(min_length=1, max_length=10000)
    cat: str = Field(min_length=1, max_length=80)
    dur: str = Field(min_length=1, max_length=120)
    date: str = Field(min_length=1, max_length=120)
    lvl: str = Field(min_length=1, max_length=120)
    fee: str = Field(min_length=1, max_length=120)
    certs: str = Field(max_length=500)
    img: str = Field(max_length=1000)
    sourceUrl: str = Field(max_length=1000)

class ProgramCreate(ProgramBase):
    pass

class Program(ProgramBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# --- Event Schemas ---
class EventBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    date: str = Field(min_length=1, max_length=120)
    type: str = Field(min_length=1, max_length=80)
    cat: str = Field(min_length=1, max_length=80)
    desc: str = Field(min_length=1, max_length=10000)
    color: str = Field(max_length=80)
    img: str = Field(max_length=1000)
    link: Optional[str] = Field(default=None, max_length=1000)

class EventCreate(EventBase):
    pass

class Event(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# --- Article Schemas ---
class ArticleBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    excerpt: str = Field(min_length=1, max_length=2000)
    content: str = Field(min_length=1, max_length=50000)
    cat: str = Field(min_length=1, max_length=80)
    catLabel: str = Field(min_length=1, max_length=120)
    date: str = Field(min_length=1, max_length=120)
    read: str = Field(max_length=40)
    author: str = Field(min_length=1, max_length=160)
    img: str = Field(max_length=1000)
    featured: bool = False

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ResearchClusterBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    desc: str = Field(min_length=1, max_length=10000)
    lead: str = Field(min_length=1, max_length=160)
    icon: str = Field(default="FlaskConical", max_length=80)


class ResearchClusterCreate(ResearchClusterBase):
    pass


class ResearchCluster(ResearchClusterBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PublicationBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    authors: str = Field(min_length=1, max_length=500)
    venue: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=80)
    link: Optional[str] = Field(default=None, max_length=1000)


class PublicationCreate(PublicationBase):
    pass


class Publication(PublicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class GalleryItemBase(BaseModel):
    caption: str = Field(min_length=1, max_length=255)
    img: str = Field(min_length=1, max_length=1000)


class GalleryItemCreate(GalleryItemBase):
    pass


class GalleryItem(GalleryItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MediaAsset(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    original_name: str
    content_type: str
    size_bytes: int
    created_at: datetime
    url: str


class CorporateServiceBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    desc: str = Field(min_length=1, max_length=3000)
    icon: str = Field(default="Building2", max_length=80)


class CorporateServiceCreate(CorporateServiceBase):
    pass


class CorporateService(CorporateServiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CorporateMetricBase(BaseModel):
    value: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=160)


class CorporateMetricCreate(CorporateMetricBase):
    pass


class CorporateMetric(CorporateMetricBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CorporateInquiryCreate(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    contact_name: str = Field(min_length=1, max_length=160)
    email: EmailStr
    team_size: str = Field(min_length=1, max_length=80)


class CorporateInquiry(CorporateInquiryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

# --- ContactMessage Schemas ---
class ContactMessageBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=40)
    program: Optional[str] = Field(default=None, max_length=255)
    message: str = Field(min_length=1, max_length=10000)

class ContactMessageCreate(ContactMessageBase):
    pass

class ContactMessage(ContactMessageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

# --- Application Schemas ---
class ApplicationBase(BaseModel):
    fullName: str = Field(min_length=1, max_length=160)
    email: EmailStr
    phone: str = Field(min_length=3, max_length=40)
    location: str = Field(min_length=1, max_length=160)
    program: str = Field(min_length=1, max_length=255)
    classFormat: str = Field(min_length=1, max_length=80)
    studyMode: str = Field(min_length=1, max_length=80)
    paymentPlan: str = Field(min_length=1, max_length=80)
    startDate: Optional[str] = Field(default=None, max_length=40)
    experienceLevel: str = Field(min_length=1, max_length=80)
    notes: Optional[str] = Field(default=None, max_length=10000)

class ApplicationCreate(ApplicationBase):
    pass

class Application(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
