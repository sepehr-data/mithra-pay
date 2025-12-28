# app/interfaces/http/controllers/cart_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.cart_sqlalchemy import SQLAlchemyCartRepository
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.services.cart_service import CartService
from app.core.exceptions import AppError

cart_bp = Blueprint("cart", __name__)


@cart_bp.get("/<int:user_id>")
def get_cart(user_id: int):
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo=cart_repo, product_repo=product_repo)

        cart = svc.get_cart(user_id)
        return jsonify(svc.to_dict(cart))
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@cart_bp.post("/items")
def add_cart_item():
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo=cart_repo, product_repo=product_repo)

        data = request.get_json() or {}
        cart = svc.add_item(
            user_id=data.get("user_id"),
            product_id=data.get("product_id"),
            quantity=int(data.get("quantity", 1)),
        )
        return jsonify(svc.to_dict(cart)), 201
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@cart_bp.put("/items/<int:item_id>")
def update_cart_item(item_id: int):
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo=cart_repo, product_repo=product_repo)

        data = request.get_json() or {}
        cart = svc.update_item(item_id=item_id, quantity=int(data.get("quantity", 1)))
        return jsonify(svc.to_dict(cart))
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@cart_bp.delete("/items/<int:item_id>")
def remove_cart_item(item_id: int):
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo=cart_repo, product_repo=product_repo)

        cart = svc.remove_item(item_id)
        return jsonify(svc.to_dict(cart))
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@cart_bp.delete("/<int:user_id>")
def clear_cart(user_id: int):
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo=cart_repo, product_repo=product_repo)

        svc.clear_cart(user_id)
        cart = svc.get_cart(user_id)
        return jsonify(svc.to_dict(cart))
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
