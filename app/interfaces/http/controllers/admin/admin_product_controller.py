# app/interfaces/http/controllers/admin_controller
from flask import Blueprint, request, jsonify
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.entities.product import Product
from app.interfaces.http.controllers.admin import _get_claims_or_401

from app.core.exceptions import AppError

admin_products_bp = Blueprint("admin_products", __name__)


def _to_float(v):
    try:
        return float(v) if v is not None else None
    except Exception:
        return None


@admin_products_bp.get("")
def admin_list_products():
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if limit <= 0 or limit > 100:
        return jsonify({"error": "limit must be between 1 and 100"}), 400
    if offset < 0:
        return jsonify({"error": "offset must be >= 0"}), 400

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)

        products = repo.list_products(is_active=None, limit=limit, offset=offset)
        total = repo.count_products()

        return jsonify({
            "items": [
                {
                    "id": p.id,
                    "title": p.title,
                    "price": _to_float(p.price),
                    "is_active": p.is_active,
                    "category_id": p.category_id,
                    "image_url": p.image_url,
                    "created_at": p.created_at.isoformat() if p.created_at else None,

                    "duration_type_id": getattr(p, "duration_type_id", None),
                    "subscription_type_id": getattr(p, "subscription_type_id", None),

                    "personal_account": getattr(p, "personal_account", False),

                    "duration": getattr(p, "duration", None),
                    "subscription_type": getattr(p, "subscription_type", None),
                }
                for p in products
            ],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "count": len(products),
                "total": total
            }
        }), 200
    finally:
        db.close()


@admin_products_bp.post("")
def admin_create_product():
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)
        data = request.get_json() or {}

        p = Product(
            title=data.get("title"),
            slug=data.get("slug"),
            category_id=data.get("category_id"),
            price=data.get("price", 0),
            compare_at_price=data.get("compare_at_price"),
            delivery_type=data.get("delivery_type"),
            platform=data.get("platform"),

            duration_type_id=data.get("duration_type_id"),
            subscription_type_id=data.get("subscription_type_id"),

            personal_account=data.get("personal_account", False),

            duration=data.get("duration"),
            subscription_type=data.get("subscription_type"),

            region=data.get("region"),
            stock=data.get("stock"),
            is_active=data.get("is_active", True),
            image_url=data.get("image_url"),
            short_description=data.get("short_description"),
            description=data.get("description"),
        )

        created = repo.create(p)
        return jsonify({"id": created.id}), 201

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@admin_products_bp.get("/<int:product_id>")
def admin_get_product(product_id: int):
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)
        p = repo.get_by_id(product_id)
        if not p:
            return jsonify({"error": "not found"}), 404

        payload = {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "category_id": p.category_id,
            "price": _to_float(p.price),
            "compare_at_price": _to_float(p.compare_at_price),
            "delivery_type": p.delivery_type,
            "platform": p.platform,

            "duration_type_id": getattr(p, "duration_type_id", None),
            "subscription_type_id": getattr(p, "subscription_type_id", None),

            "personal_account": getattr(p, "personal_account", False),

            "duration": getattr(p, "duration", None),
            "subscription_type": getattr(p, "subscription_type", None),

            "region": p.region,
            "stock": p.stock,
            "is_active": p.is_active,
            "image_url": p.image_url,
            "short_description": p.short_description,
            "description": p.description,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }

        dt = getattr(p, "duration_type", None)
        if dt is not None:
            payload["duration_type"] = {"id": dt.id, "title": dt.title, "slug": dt.slug}

        st = getattr(p, "subscription_type_rel", None)
        if st is not None:
            payload["subscription_type"] = {"id": st.id, "title": st.title, "slug": st.slug}

        return jsonify(payload), 200
    finally:
        db.close()


@admin_products_bp.put("/<int:product_id>")
def admin_update_product(product_id: int):
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)
        p = repo.get_by_id(product_id)
        if not p:
            return jsonify({"error": "not found"}), 404

        data = request.get_json() or {}

        p.title = data.get("title", p.title)
        p.slug = data.get("slug", p.slug)
        p.category_id = data.get("category_id", p.category_id)
        p.price = data.get("price", p.price)
        p.compare_at_price = data.get("compare_at_price", p.compare_at_price)
        p.delivery_type = data.get("delivery_type", p.delivery_type)
        p.platform = data.get("platform", p.platform)

        if "duration_type_id" in data:
            p.duration_type_id = data.get("duration_type_id")
        if "subscription_type_id" in data:
            p.subscription_type_id = data.get("subscription_type_id")
        if "personal_account" in data:
            p.personal_account = data.get("personal_account")

        # ⚠️ legacy (اختیاری)
        if "duration" in data:
            p.duration = data.get("duration")
        if "subscription_type" in data:
            p.subscription_type = data.get("subscription_type")

        p.region = data.get("region", p.region)
        p.stock = data.get("stock", p.stock)
        p.is_active = data.get("is_active", p.is_active)
        p.image_url = data.get("image_url", p.image_url)
        p.short_description = data.get("short_description", p.short_description)
        p.description = data.get("description", p.description)

        updated = repo.update(p)
        return jsonify({"id": updated.id}), 200
    finally:
        db.close()


@admin_products_bp.delete("/<int:product_id>")
def admin_delete_product(product_id: int):
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)
        product = repo.get_by_id(product_id)
        if not product:
            return jsonify({"error": "محصول پیدا نشد"}), 404

        repo.delete(product_id)
        return jsonify({"success": True, "message": "محصول با موفقیت حذف شد"}), 200
    finally:
        db.close()
