# app/interfaces/http/controllers/admin_banners_controller.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.banner_sqlalchemy import SQLAlchemyBannerRepository
from app.domain.entities.banner import Banner
from app.core.exceptions import AppError
from app.interfaces.http.controllers.admin import _get_claims_or_401

admin_banners_bp = Blueprint("admin_banners", __name__)


def parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


@admin_banners_bp.post("")
def admin_create_banner():
    db = get_db()
    try:
        repo = SQLAlchemyBannerRepository(db)
        data = request.get_json() or {}

        banner = Banner(
            title=data["title"],
            link=data.get("link"),
            image_url=data["image_url"],
            status=data.get("status", "ACTIVE"),
        )

        created = repo.create(banner)
        return jsonify({"id": created.id}), 201
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@admin_banners_bp.put("/<int:banner_id>")
def admin_update_banner(banner_id: int):
    db = get_db()
    try:
        repo = SQLAlchemyBannerRepository(db)
        existing_banner = repo.get_by_id(banner_id)
        if not existing_banner:
            return jsonify({"error": "بنر پیدا نشد"}), 404

        data = request.get_json() or {}

        existing_banner.title = data.get("title", existing_banner.title)
        existing_banner.link = data.get("link", existing_banner.link)
        existing_banner.image_url = data.get("image_url", existing_banner.image_url)
        existing_banner.status = data.get("status", existing_banner.status)

        updated = repo.update(existing_banner)
        return jsonify({"id": updated.id}), 200
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@admin_banners_bp.get("")
def admin_list_banners():
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyBannerRepository(db)
        banners = repo.list(limit=200, offset=0)

        return jsonify([
            {
                "id": b.id,
                "title": b.title,
                "link": b.link,
                "image_url": b.image_url,
                "status": b.status,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "updated_at": b.updated_at.isoformat() if b.updated_at else None,
            }
            for b in banners
        ])
    finally:
        db.close()


@admin_banners_bp.get("/<int:banner_id>")
def admin_get_banner(banner_id: int):
    db = get_db()
    try:
        repo = SQLAlchemyBannerRepository(db)
        banner = repo.get_by_id(banner_id)
        if not banner:
            return jsonify({"error": "بنر پیدا نشد"}), 404

        return jsonify({
            "id": banner.id,
            "title": banner.title,
            "link": banner.link,
            "image_url": banner.image_url,
            "status": banner.status,
            "created_at": banner.created_at.isoformat() if banner.created_at else None,
            "updated_at": banner.updated_at.isoformat() if banner.updated_at else None,
        }), 200
    finally:
        db.close()


@admin_banners_bp.delete("/<int:banner_id>")
def admin_delete_banner(banner_id: int):
    db = get_db()
    try:
        repo = SQLAlchemyBannerRepository(db)
        banner = repo.get_by_id(banner_id)
        if not banner:
            return jsonify({"error": "بنر پیدا نشد"}), 404

        repo.delete(banner_id)
        return jsonify({"id": banner_id, "deleted": True}), 200
    finally:
        db.close()
