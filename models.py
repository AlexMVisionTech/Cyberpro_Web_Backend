from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    desc = Column(Text)
    cat = Column(String, index=True) # foundation, intermediate, advanced, expert
    dur = Column(String)
    date = Column(String)
    lvl = Column(String)
    fee = Column(String)
    certs = Column(String)
    img = Column(String)
    sourceUrl = Column(String)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    date = Column(String)
    type = Column(String) # Hackathon, Webinar, Bootcamp
    cat = Column(String, index=True) # ctf, webinar, bootcamp
    desc = Column(Text)
    color = Column(String)
    img = Column(String)
    link = Column(String, nullable=True)

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    excerpt = Column(Text)
    content = Column(Text)
    cat = Column(String, index=True)
    catLabel = Column(String)
    date = Column(String)
    read = Column(String)
    author = Column(String)
    img = Column(String)
    featured = Column(Boolean, default=False)


class ResearchCluster(Base):
    __tablename__ = "research_clusters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    desc = Column(Text)
    lead = Column(String)
    icon = Column(String, default="FlaskConical")


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(String)
    venue = Column(String)
    type = Column(String)
    link = Column(String, nullable=True)


class GalleryItem(Base):
    __tablename__ = "gallery_items"

    id = Column(Integer, primary_key=True, index=True)
    caption = Column(String)
    img = Column(String)


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    original_name = Column(String)
    content_type = Column(String)
    size_bytes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class CorporateService(Base):
    __tablename__ = "corporate_services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    desc = Column(Text)
    icon = Column(String, default="Building2")


class CorporateMetric(Base):
    __tablename__ = "corporate_metrics"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)
    label = Column(String)


class CorporateInquiry(Base):
    __tablename__ = "corporate_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String)
    contact_name = Column(String)
    email = Column(String)
    team_size = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String, nullable=True)
    program = Column(String, nullable=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    fullName = Column(String)
    email = Column(String)
    phone = Column(String)
    location = Column(String)
    program = Column(String)
    classFormat = Column(String)
    studyMode = Column(String)
    paymentPlan = Column(String)
    startDate = Column(String, nullable=True)
    experienceLevel = Column(String)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
