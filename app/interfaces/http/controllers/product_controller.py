# app/interfaces/http/controllers/product_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.services.product_service import ProductService
from app.core.exceptions import AppError

product_bp = Blueprint("products", __name__)


@product_bp.post("/")
def create_product():
    db = get_db()
    try:
        product_repo = SQLAlchemyProductRepository(db)
        svc = ProductService(product_repo=product_repo)

        data = request.get_json() or {}
        product = svc.create_product(
            title=data.get("title"),
            slug=data.get("slug"),
            category_id=data.get("category_id"),
            price=data.get("price"),
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

        return jsonify(svc.to_dict(product)), 201
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@product_bp.get("/")
def list_products():
    db = get_db()
    try:
        product_repo = SQLAlchemyProductRepository(db)
        svc = ProductService(product_repo=product_repo)

        category = request.args.get("category")
        search = request.args.get("search")

        duration_type_id = request.args.get("duration_type_id", type=int)
        subscription_type_id = request.args.get("subscription_type_id", type=int)
        personal_account = request.args.get("personal_account")
        if personal_account is not None:
            personal_account = personal_account.lower() in ("1", "true", "yes", "on")

        items = svc.list_products(
            category_slug=category,
            search=search,
            is_active=True,
            limit=50,
            offset=0,
            duration_type_id=duration_type_id,
            subscription_type_id=subscription_type_id,
            personal_account=personal_account,
        )
        return jsonify([svc.to_dict(p) for p in items])
    finally:
        db.close()


@product_bp.get("/top-weekly")
def get_top_weekly_products():
    db = get_db()
    try:
        limit = request.args.get("limit", default=8, type=int)

        product_repo = SQLAlchemyProductRepository(db)
        svc = ProductService(product_repo=product_repo)

        products = svc.get_top_selling_products_this_week(limit=limit)
        data = [svc.to_dict(p) for p in products]

        return jsonify({"items": data, "count": len(data)})
    finally:
        db.close()


@product_bp.get("/<int:product_id>")
def get_product(product_id: int):
    db = get_db()
    try:
        product_repo = SQLAlchemyProductRepository(db)
        svc = ProductService(product_repo=product_repo)

        p = svc.get_product(product_id)
        return jsonify(svc.to_dict(p))
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
