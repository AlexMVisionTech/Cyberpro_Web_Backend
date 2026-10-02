"""Cyberpro Global public website and administration API."""

from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Request, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import auth
import models
import schemas
from database import engine, get_db

logger = logging.getLogger("cyberpro.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize schema for the lightweight SQLite deployment."""
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Cyberpro Global API",
    description="Public content and secure administration services for Cyberpro Global.",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT", "development").lower() != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

MEDIA_DIR = Path(os.getenv("MEDIA_DIR", str(Path(__file__).with_name("uploads")))).resolve()
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

environment = os.getenv("ENVIRONMENT", "development").lower()
origins = [origin.strip().rstrip("/") for origin in os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
).split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?" if environment != "production" else None,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["system"])
def read_root():
    return {"name": "Cyberpro Global API", "version": app.version, "docs": "/docs" if app.docs_url else None}


@app.get("/health", tags=["system"])
def health_check(db: Session = Depends(get_db)):
    """Check application and database availability without exposing internals."""
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as exc:
        logger.exception("Health check failed")
        raise HTTPException(status_code=503, detail="Service unavailable") from exc
    return {"status": "ok"}


def _commit(db: Session):
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Database transaction failed")
        raise HTTPException(status_code=500, detail="Unable to save changes")


def _delete_or_404(db: Session, model, item_id: int, label: str):
    item = db.query(model).filter(model.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    db.delete(item)
    _commit(db)


@app.post("/api/admin/login", response_model=schemas.Token, tags=["admin"])
def login_admin(form_data: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin_user = db.query(models.AdminUser).filter(models.AdminUser.username == form_data.username).first()
    if not admin_user or not auth.verify_password(form_data.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": auth.create_access_token(data={"sub": admin_user.username}), "token_type": "bearer"}


@app.get("/api/admin/me", response_model=schemas.AdminUser, tags=["admin"])
def get_admin_me(current_admin: models.AdminUser = Depends(auth.get_current_admin)):
    return current_admin


@app.get("/api/programs", response_model=List[schemas.Program], tags=["programs"])
def get_programs(db: Session = Depends(get_db)):
    return db.query(models.Program).order_by(models.Program.id).all()


@app.post("/api/programs", response_model=schemas.Program, status_code=201, tags=["programs"])
def create_program(program: schemas.ProgramCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    item = models.Program(**program.model_dump())
    db.add(item)
    _commit(db)
    db.refresh(item)
    return item


@app.put("/api/programs/{id}", response_model=schemas.Program, tags=["programs"])
def update_program(id: int, program: schemas.ProgramCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    item = db.query(models.Program).filter(models.Program.id == id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Program not found")
    for key, value in program.model_dump().items():
        setattr(item, key, value)
    _commit(db)
    db.refresh(item)
    return item


@app.delete("/api/programs/{id}", status_code=204, tags=["programs"])
def delete_program(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.Program, id, "Program")
    return Response(status_code=204)


@app.get("/api/events", response_model=List[schemas.Event], tags=["events"])
def get_events(db: Session = Depends(get_db)):
    return db.query(models.Event).order_by(models.Event.id).all()


@app.post("/api/events", response_model=schemas.Event, status_code=201, tags=["events"])
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    item = models.Event(**event.model_dump())
    db.add(item)
    _commit(db)
    db.refresh(item)
    return item


@app.put("/api/events/{id}", response_model=schemas.Event, tags=["events"])
def update_event(id: int, event: schemas.EventCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    item = db.query(models.Event).filter(models.Event.id == id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.model_dump().items():
        setattr(item, key, value)
    _commit(db)
    db.refresh(item)
    return item


@app.delete("/api/events/{id}", status_code=204, tags=["events"])
def delete_event(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.Event, id, "Event")
    return Response(status_code=204)


@app.get("/api/articles", response_model=List[schemas.Article], tags=["articles"])
def get_articles(db: Session = Depends(get_db)):
    return db.query(models.Article).order_by(models.Article.id.desc()).all()


@app.post("/api/articles", response_model=schemas.Article, status_code=201, tags=["articles"])
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    item = models.Article(**article.model_dump())
    db.add(item)
    _commit(db)
    db.refresh(item)
    return item


@app.put("/api/articles/{id}", response_model=schemas.Article, tags=["articles"])
def update_article(id: int, article: schemas.ArticleCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    item = db.query(models.Article).filter(models.Article.id == id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Article not found")
    for key, value in article.model_dump().items():
        setattr(item, key, value)
    _commit(db)
    db.refresh(item)
    return item


@app.delete("/api/articles/{id}", status_code=204, tags=["articles"])
def delete_article(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.Article, id, "Article")
    return Response(status_code=204)


@app.get("/api/research/clusters", response_model=List[schemas.ResearchCluster], tags=["research"])
def get_research_clusters(db: Session = Depends(get_db)):
    return db.query(models.ResearchCluster).order_by(models.ResearchCluster.id).all()


@app.post("/api/research/clusters", response_model=schemas.ResearchCluster, status_code=201, tags=["research"])
def create_research_cluster(item: schemas.ResearchClusterCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = models.ResearchCluster(**item.model_dump())
    db.add(record)
    _commit(db)
    db.refresh(record)
    return record


@app.put("/api/research/clusters/{id}", response_model=schemas.ResearchCluster, tags=["research"])
def update_research_cluster(id: int, item: schemas.ResearchClusterCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = db.query(models.ResearchCluster).filter(models.ResearchCluster.id == id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Research cluster not found")
    for key, value in item.model_dump().items():
        setattr(record, key, value)
    _commit(db)
    db.refresh(record)
    return record


@app.delete("/api/research/clusters/{id}", status_code=204, tags=["research"])
def delete_research_cluster(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.ResearchCluster, id, "Research cluster")
    return Response(status_code=204)


@app.get("/api/research/publications", response_model=List[schemas.Publication], tags=["research"])
def get_publications(db: Session = Depends(get_db)):
    return db.query(models.Publication).order_by(models.Publication.id).all()


@app.post("/api/research/publications", response_model=schemas.Publication, status_code=201, tags=["research"])
def create_publication(item: schemas.PublicationCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = models.Publication(**item.model_dump())
    db.add(record)
    _commit(db)
    db.refresh(record)
    return record


@app.put("/api/research/publications/{id}", response_model=schemas.Publication, tags=["research"])
def update_publication(id: int, item: schemas.PublicationCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = db.query(models.Publication).filter(models.Publication.id == id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    for key, value in item.model_dump().items():
        setattr(record, key, value)
    _commit(db)
    db.refresh(record)
    return record


@app.delete("/api/research/publications/{id}", status_code=204, tags=["research"])
def delete_publication(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.Publication, id, "Publication")
    return Response(status_code=204)


@app.get("/api/gallery", response_model=List[schemas.GalleryItem], tags=["gallery"])
def get_gallery(db: Session = Depends(get_db)):
    return db.query(models.GalleryItem).order_by(models.GalleryItem.id).all()


@app.post("/api/gallery", response_model=schemas.GalleryItem, status_code=201, tags=["gallery"])
def create_gallery_item(item: schemas.GalleryItemCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = models.GalleryItem(**item.model_dump())
    db.add(record)
    _commit(db)
    db.refresh(record)
    return record


@app.put("/api/gallery/{id}", response_model=schemas.GalleryItem, tags=["gallery"])
def update_gallery_item(id: int, item: schemas.GalleryItemCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = db.query(models.GalleryItem).filter(models.GalleryItem.id == id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    record.caption = item.caption
    record.img = item.img
    _commit(db)
    db.refresh(record)
    return record


@app.delete("/api/gallery/{id}", status_code=204, tags=["gallery"])
def delete_gallery_item(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.GalleryItem, id, "Gallery item")
    return Response(status_code=204)


@app.get("/api/corporate/services", response_model=List[schemas.CorporateService], tags=["corporate"])
def get_corporate_services(db: Session = Depends(get_db)):
    return db.query(models.CorporateService).order_by(models.CorporateService.id).all()


@app.post("/api/corporate/services", response_model=schemas.CorporateService, status_code=201, tags=["corporate"])
def create_corporate_service(item: schemas.CorporateServiceCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = models.CorporateService(**item.model_dump())
    db.add(record)
    _commit(db)
    db.refresh(record)
    return record


@app.put("/api/corporate/services/{id}", response_model=schemas.CorporateService, tags=["corporate"])
def update_corporate_service(id: int, item: schemas.CorporateServiceCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = db.query(models.CorporateService).filter(models.CorporateService.id == id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Corporate service not found")
    for key, value in item.model_dump().items():
        setattr(record, key, value)
    _commit(db)
    db.refresh(record)
    return record


@app.delete("/api/corporate/services/{id}", status_code=204, tags=["corporate"])
def delete_corporate_service(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.CorporateService, id, "Corporate service")
    return Response(status_code=204)


@app.get("/api/corporate/metrics", response_model=List[schemas.CorporateMetric], tags=["corporate"])
def get_corporate_metrics(db: Session = Depends(get_db)):
    return db.query(models.CorporateMetric).order_by(models.CorporateMetric.id).all()


@app.post("/api/corporate/metrics", response_model=schemas.CorporateMetric, status_code=201, tags=["corporate"])
def create_corporate_metric(item: schemas.CorporateMetricCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = models.CorporateMetric(**item.model_dump())
    db.add(record)
    _commit(db)
    db.refresh(record)
    return record


@app.put("/api/corporate/metrics/{id}", response_model=schemas.CorporateMetric, tags=["corporate"])
def update_corporate_metric(id: int, item: schemas.CorporateMetricCreate, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    record = db.query(models.CorporateMetric).filter(models.CorporateMetric.id == id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Corporate metric not found")
    record.value = item.value
    record.label = item.label
    _commit(db)
    db.refresh(record)
    return record


@app.delete("/api/corporate/metrics/{id}", status_code=204, tags=["corporate"])
def delete_corporate_metric(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.CorporateMetric, id, "Corporate metric")
    return Response(status_code=204)


@app.post("/api/corporate/inquiries", response_model=schemas.CorporateInquiry, status_code=201, tags=["corporate"])
def submit_corporate_inquiry(item: schemas.CorporateInquiryCreate, db: Session = Depends(get_db)):
    record = models.CorporateInquiry(**item.model_dump())
    db.add(record)
    _commit(db)
    db.refresh(record)
    return record


@app.get("/api/corporate/inquiries", response_model=List[schemas.CorporateInquiry], tags=["corporate"])
def get_corporate_inquiries(db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    return db.query(models.CorporateInquiry).order_by(models.CorporateInquiry.created_at.desc()).all()


@app.delete("/api/corporate/inquiries/{id}", status_code=204, tags=["corporate"])
def delete_corporate_inquiry(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.CorporateInquiry, id, "Corporate inquiry")
    return Response(status_code=204)


MEDIA_TYPES = {
    "image/jpeg": (".jpg", (b"\xff\xd8\xff",)),
    "image/png": (".png", (b"\x89PNG\r\n\x1a\n",)),
    "image/webp": (".webp", (b"RIFF",)),
    "image/gif": (".gif", (b"GIF87a", b"GIF89a")),
}
MAX_IMAGE_BYTES = 10 * 1024 * 1024


def _media_url(filename: str, request: Request) -> str:
    base_url = os.getenv("MEDIA_BASE_URL", str(request.base_url).rstrip("/"))
    return f"{base_url.rstrip('/')}/media/{filename}"


def _media_payload(asset: models.MediaAsset, request: Request):
    return {"id": asset.id, "filename": asset.filename, "original_name": asset.original_name,
            "content_type": asset.content_type, "size_bytes": asset.size_bytes,
            "created_at": asset.created_at, "url": _media_url(asset.filename, request)}


@app.get("/api/media", response_model=List[schemas.MediaAsset], tags=["media"])
def list_media(request: Request, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    assets = db.query(models.MediaAsset).order_by(models.MediaAsset.created_at.desc()).all()
    return [_media_payload(asset, request) for asset in assets]


@app.post("/api/media", response_model=schemas.MediaAsset, status_code=201, tags=["media"])
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: models.AdminUser = Depends(auth.get_current_admin),
):
    media_type = (file.content_type or "").lower()
    media_spec = MEDIA_TYPES.get(media_type)
    if media_spec is None:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, WebP, or GIF image")

    contents = await file.read(MAX_IMAGE_BYTES + 1)
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller")
    extension, signatures = media_spec
    if not any(contents.startswith(signature) for signature in signatures):
        raise HTTPException(status_code=415, detail="The file contents do not match the selected image type")
    if media_type == "image/webp" and contents[8:12] != b"WEBP":
        raise HTTPException(status_code=415, detail="The file contents do not match the selected image type")

    filename = f"{uuid4().hex}{extension}"
    destination = MEDIA_DIR / filename
    try:
        destination.write_bytes(contents)
        asset = models.MediaAsset(
            filename=filename,
            original_name=Path(file.filename or "image").name[:255],
            content_type=media_type,
            size_bytes=len(contents),
        )
        db.add(asset)
        _commit(db)
        db.refresh(asset)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    return _media_payload(asset, request)


@app.delete("/api/media/{id}", status_code=204, tags=["media"])
def delete_media(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    asset = db.query(models.MediaAsset).filter(models.MediaAsset.id == id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Image not found")
    filename = asset.filename
    db.delete(asset)
    _commit(db)
    (MEDIA_DIR / filename).unlink(missing_ok=True)
    return Response(status_code=204)


@app.post("/api/contact", response_model=schemas.ContactMessage, status_code=201, tags=["contact"])
def submit_contact(contact: schemas.ContactMessageCreate, db: Session = Depends(get_db)):
    item = models.ContactMessage(**contact.model_dump())
    db.add(item)
    _commit(db)
    db.refresh(item)
    return item


@app.get("/api/contact", response_model=List[schemas.ContactMessage], tags=["contact"])
def get_contacts(db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    return db.query(models.ContactMessage).order_by(models.ContactMessage.created_at.desc()).all()


@app.delete("/api/contact/{id}", status_code=204, tags=["contact"])
def delete_contact(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.ContactMessage, id, "Contact message")
    return Response(status_code=204)


@app.post("/api/applications", response_model=schemas.Application, status_code=201, tags=["applications"])
def submit_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    item = models.Application(**application.model_dump())
    db.add(item)
    _commit(db)
    db.refresh(item)
    return item


@app.get("/api/applications", response_model=List[schemas.Application], tags=["applications"])
def get_applications(db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    return db.query(models.Application).order_by(models.Application.created_at.desc()).all()


@app.delete("/api/applications/{id}", status_code=204, tags=["applications"])
def delete_application(id: int, db: Session = Depends(get_db), _: models.AdminUser = Depends(auth.get_current_admin)):
    _delete_or_404(db, models.Application, id, "Application")
    return Response(status_code=204)
