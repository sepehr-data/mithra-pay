# app/interfaces/http/controllers/product_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.services.product_service import ProductService
from app.core.exceptions import AppError

product_bp = Blueprint("products", __name__)


@product_bp.get("/")
def list_products():
    db = get_db()
    try:
        product_repo = SQLAlchemyProductRepository(db)
        svc = ProductService(product_repo=product_repo)

        category = request.args.get("category")
        search = request.args.get("search")
        items = svc.list_products(
            category_slug=category,
            search=search,
            is_active=True,
            limit=50,
            offset=0,
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
