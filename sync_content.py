"""Idempotently load website events, articles, and research content into SQLite."""

import json
from pathlib import Path

import models
from database import SessionLocal, engine


CATALOGS = (
    ("events_catalog.json", models.Event),
    ("articles_catalog.json", models.Article),
    ("research_clusters.json", models.ResearchCluster),
    ("publications.json", models.Publication),
    ("gallery.json", models.GalleryItem),
    ("corporate_services.json", models.CorporateService),
    ("corporate_metrics.json", models.CorporateMetric),
)


def sync_content() -> dict[str, tuple[int, int]]:
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    counts = {}
    try:
        for filename, model in CATALOGS:
            records = json.loads(Path(__file__).with_name(filename).read_text(encoding="utf-8"))
            added = updated = 0
            for values in records:
                identity_field = (
                    "caption" if model is models.GalleryItem
                    else "label" if model is models.CorporateMetric
                    else "title"
                )
                record = db.query(model).filter(getattr(model, identity_field) == values[identity_field]).first()
                if record is None:
                    db.add(model(**values))
                    added += 1
                else:
                    for key, value in values.items():
                        setattr(record, key, value)
                    updated += 1
            counts[filename] = (added, updated)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return counts


if __name__ == "__main__":
    for catalog, (added, updated) in sync_content().items():
        print(f"{catalog}: {added} added, {updated} refreshed")
