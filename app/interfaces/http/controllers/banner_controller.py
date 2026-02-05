# app/interfaces/http/controllers/banner_controller.py
from flask import Blueprint, jsonify, request
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.banner_sqlalchemy import SQLAlchemyBannerRepository

banners_bp = Blueprint("banners", __name__)


def _banner_to_dict(banner):
    return {
        "id": banner.id,
        "title": banner.title,
        "link": banner.link,
        "image_url": banner.image_url,
        "status": banner.status,
        "created_at": banner.created_at.isoformat() if banner.created_at else None,
        "updated_at": banner.updated_at.isoformat() if banner.updated_at else None,
    }


@banners_bp.get("")
def list_active_banners():

    db = get_db()
    try:
        repo = SQLAlchemyBannerRepository(db)
        banners = repo.list_active() if hasattr(repo, "list_active") else repo.list()

        out = []
        for b in (banners or []):
            if str(getattr(b, "status", "")).lower() in ("active", "enabled", "1", "true"):
                out.append(_banner_to_dict(b))

        return jsonify(out), 200
    finally:
        db.close()


@banners_bp.get("/<int:banner_id>")
def get_banner(banner_id: int):

    db = get_db()
    try:
        repo = SQLAlchemyBannerRepository(db)
        banner = repo.get_by_id(banner_id)
        if not banner:
            return jsonify({"error": "بنر پیدا نشد"}), 404

        if str(getattr(banner, "status", "")).lower() not in ("active", "enabled", "1", "true"):
            return jsonify({"error": "بنر غیر فعال است"}), 404

        return jsonify(_banner_to_dict(banner)), 200
    finally:
        db.close()
