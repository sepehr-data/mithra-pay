# app/interfaces/http/controllers/admin_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.entities.product import Product
from app.core.exceptions import AppError
from app.core.security import decode_access_token, require_roles

admin_bp = Blueprint("admin", __name__)


def _get_claims_or_401():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    claims = decode_access_token(token)
    # require admin
    require_roles(claims, ["admin"])
    return claims


@admin_bp.get("/products")
def admin_list_products():
    try:
        _get_claims_or_401()
    except Exception as e:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)
        products = repo.list_products(is_active=None, limit=200, offset=0)
        return jsonify([
            {
                "id": p.id,
                "title": p.title,
                "price": float(p.price),
                "is_active": p.is_active,
            } for p in products
        ])
    finally:
        db.close()


@admin_bp.post("/products")
def admin_create_product():
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
            duration=data.get("duration"),
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


@admin_bp.put("/products/<int:product_id>")
def admin_update_product(product_id: int):
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
        p.duration = data.get("duration", p.duration)
        p.region = data.get("region", p.region)
        p.stock = data.get("stock", p.stock)
        p.is_active = data.get("is_active", p.is_active)
        p.image_url = data.get("image_url", p.image_url)
        p.short_description = data.get("short_description", p.short_description)
        p.description = data.get("description", p.description)

        updated = repo.update(p)
        return jsonify({"id": updated.id})
    finally:
        db.close()
