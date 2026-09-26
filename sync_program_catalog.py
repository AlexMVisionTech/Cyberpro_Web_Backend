"""Idempotently load the public website course catalog into the API database."""

import json
from pathlib import Path

import models
from database import SessionLocal, engine


def sync_catalog() -> tuple[int, int]:
    catalog_path = Path(__file__).with_name("program_catalog.json")
    programs = json.loads(catalog_path.read_text(encoding="utf-8"))
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    inserted = updated = 0
    try:
        for data in programs:
            program = (
                db.query(models.Program)
                .filter(models.Program.title == data["title"], models.Program.cat == data["cat"])
                .first()
            )
            if program is None:
                db.add(models.Program(**data))
                inserted += 1
            else:
                for key, value in data.items():
                    setattr(program, key, value)
                updated += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return inserted, updated


if __name__ == "__main__":
    created, refreshed = sync_catalog()
    print(f"Course catalog synced: {created} added, {refreshed} refreshed.")
