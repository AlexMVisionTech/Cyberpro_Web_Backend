import os

from database import engine, SessionLocal
import models
import auth
from sync_program_catalog import sync_catalog
from sync_content import sync_content

EVENTS = [
  { "title": 'Zero-Day Cyber Defense CTF', "date": 'Aug 15, 2026', "type": 'Hackathon', "cat": 'ctf', "desc": 'Breach isolated virtual environments, capture dynamic flags, and earn points on the leaderboard.', "color": 'badge-blue', "img": '/images/events/ctf-cyber-defense.svg', "link": None },
  { "title": 'Generative AI Security Pipelines', "date": 'Sep 02, 2026', "type": 'Webinar', "cat": 'webinar', "desc": 'Learn safe prompt parsing and hardening pipelines against model poisoning with guest speakers.', "color": 'badge-orange', "img": '/images/events/ai-security-webinar.svg', "link": None },
]

ARTICLES = [
  { "title": 'Implementing Zero-Trust Architecture in Legacy Enterprise Infrastructure', "excerpt": 'Explore concrete pathways to migrate older networks to zero-trust segments using micro-segmentations.', "content": 'Full content goes here...', "cat": 'security', "catLabel": 'Cybersecurity', "date": 'August 1, 2026', "read": '6 min', "author": 'Dr. Philip Mulwa', "img": '/images/blog_1.jpg', "featured": True },
  { "title": 'Model Adversarial Defense: Hardening ML Classifiers', "excerpt": 'A technical breakdown of threat mechanisms attacking image recognition systems with adversarial feeds.', "content": 'Full content goes here...', "cat": 'ai', "catLabel": 'Artificial Intelligence', "date": 'July 28, 2026', "read": '8 min', "author": 'Prof. Janet Okoth', "img": '/images/blog_2.jpg', "featured": False },
]

def seed_data():
    added, refreshed = sync_catalog()
    print(f"Course catalog synced: {added} added, {refreshed} refreshed.")
    for catalog, (created, updated) in sync_content().items():
        print(f"{catalog}: {created} added, {updated} refreshed.")
    db = SessionLocal()
    
    # Seed admin user
    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_username or not admin_password:
        raise RuntimeError("Set ADMIN_USERNAME and ADMIN_PASSWORD before seeding the administrator")
    admin_username = admin_username.strip().lower()
    if not admin_username.endswith("@cyberpro.ke"):
        raise RuntimeError("ADMIN_USERNAME must use a @cyberpro.ke email address")
    admin_user = db.query(models.AdminUser).filter_by(username=admin_username).first()
    if not admin_user:
        print("Seeding admin user...")
        admin_user = models.AdminUser(username=admin_username)
        db.add(admin_user)
    admin_user.hashed_password = auth.hash_password(admin_password)
    
    print("Seeding events...")
    for e in EVENTS:
        if not db.query(models.Event).filter_by(title=e["title"]).first():
            db.add(models.Event(**e))
        
    print("Seeding articles...")
    for a in ARTICLES:
        if not db.query(models.Article).filter_by(title=a["title"]).first():
            db.add(models.Article(**a))
        
    try:
        db.commit()
        print("Seed complete.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables are created
    models.Base.metadata.create_all(bind=engine)
    seed_data()
