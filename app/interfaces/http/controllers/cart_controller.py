# app/interfaces/http/controllers/cart_controller.py
from __future__ import annotations

from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.cart_sqlalchemy import SQLAlchemyCartRepository
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.services.cart_service import CartService
from app.core.exceptions import AppError, UnauthorizedError
from app.core.security import decode_access_token

cart_bp = Blueprint("carts", __name__)

def get_user_id_from_token() -> int:
    auth = (request.headers.get("Authorization") or "").strip()
    if not auth:
        raise UnauthorizedError("Authorization token required")
    parts = auth.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid authorization header")

    token = parts[1].strip()

    try:
        claims = decode_access_token(token)
    except Exception:
        raise UnauthorizedError("Invalid or expired token")

    raw = claims.get("user_id")
    if raw is None:
        raw = claims.get("sub")

    try:
        user_id = int(str(raw).strip())
    except Exception:
        raise UnauthorizedError("Invalid token claims")

    if user_id <= 0:
        raise UnauthorizedError("Invalid token claims")

    return user_id


def _to_float(v):
    try:
        return float(v) if v is not None else None
    except Exception:
        return None


def _cart_to_dict(cart) -> dict:
    items_out = []
    for i in (getattr(cart, "items", []) or []):
        items_out.append({
            "id": i.id,
            "product_id": i.product_id,
            "title": i.title_snapshot,
            "unit_price": _to_float(i.unit_price),
            "quantity": int(i.quantity or 0),
            "line_total": _to_float(i.line_total),
            "duration_type_id": getattr(i, "duration_type_id", None),
            "subscription_type_id": getattr(i, "subscription_type_id", None),
            "personal_account": bool(getattr(i, "personal_account", False)),
        })

    total = 0.0
    for it in items_out:
        if it["line_total"] is not None:
            total += float(it["line_total"])

    return {
        "cart_id": cart.id,
        "status": getattr(cart, "status", "ACTIVE"),
        "items": items_out,
        "count": len(items_out),
        "total": total,
    }


def _as_int(v, default=None):
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        return default


@cart_bp.get("/")
def get_cart():
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo, product_repo)

        user_id = get_user_id_from_token()

        cart = svc.get_cart(user_id)
        return jsonify(_cart_to_dict(cart)), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@cart_bp.post("/add")
def add_to_cart():
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo, product_repo)

        user_id = get_user_id_from_token()

        data = request.get_json() or {}
        product_id = _as_int(data.get("product_id"))
        if not product_id:
            return jsonify({"error": "product_id is required"}), 400

        quantity = _as_int(data.get("quantity"), default=1) or 1
        if quantity <= 0:
            quantity = 1

        duration_type_id = _as_int(data.get("duration_type_id"))
        subscription_type_id = _as_int(data.get("subscription_type_id"))
        personal_account = bool(data.get("personal_account", False))

        svc.add_item(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            duration_type_id=duration_type_id,
            subscription_type_id=subscription_type_id,
            personal_account=personal_account,
        )

        cart = svc.get_cart(user_id)
        return jsonify(_cart_to_dict(cart)), 201

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@cart_bp.delete("/remove/<int:item_id>")
def remove_from_cart(item_id: int):
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo, product_repo)

        user_id = get_user_id_from_token()

        svc.remove_item(user_id, item_id)

        cart = svc.get_cart(user_id)
        return jsonify(_cart_to_dict(cart)), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@cart_bp.post("/clear")
def clear_cart():
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo, product_repo)

        user_id = get_user_id_from_token()

        svc.clear_cart(user_id)

        cart = svc.get_cart(user_id)
        return jsonify(_cart_to_dict(cart)), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@cart_bp.patch("/items/<int:item_id>")
def update_cart_item(item_id: int):
    db = get_db()
    try:
        cart_repo = SQLAlchemyCartRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = CartService(cart_repo, product_repo)

        user_id = get_user_id_from_token()

        data = request.get_json() or {}
        quantity = _as_int(data.get("quantity"))
        if quantity is None:
            return jsonify({"error": "quantity is required"}), 400

        if quantity <= 0:
            svc.remove_item(user_id, item_id)
        else:
            svc.update_item_quantity(user_id=user_id, cart_item_id=item_id, quantity=quantity)

        cart = svc.get_cart(user_id)
        return jsonify(_cart_to_dict(cart)), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
