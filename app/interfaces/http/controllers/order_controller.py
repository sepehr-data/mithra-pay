# app/interfaces/http/controllers/order_controller.py
from flask import Blueprint, request, jsonify
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.order_sqlalchemy import SQLAlchemyOrderRepository
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.services.order_service import OrderService
from app.core.exceptions import AppError, UnauthorizedError
from app.core.security import decode_access_token
from app.infrastructure.repositories.user_sqlalchemy import SQLAlchemyUserRepository

order_bp = Blueprint("orders", __name__)

@order_bp.post("/create")
def create_order():
    db = get_db()
    try:
        order_repo = SQLAlchemyOrderRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = OrderService(order_repo=order_repo, product_repo=product_repo)

        data = request.get_json() or {}
        user_id = data.get("user_id")  # TODO: get from JWT
        items = data.get("items", [])

        order = svc.create_order(user_id=user_id, items=items)
        return jsonify({
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": float(order.total_amount),
        }), 201
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@order_bp.get("/<int:order_id>")
def get_order(order_id: int):
    db = get_db()
    try:
        order_repo = SQLAlchemyOrderRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = OrderService(order_repo=order_repo, product_repo=product_repo)

        order = svc.get_order(order_id)
        return jsonify(svc.to_dict(order))
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()

@order_bp.get("/")
def get_all_orders():
    db = get_db()
    try:
        order_repo = SQLAlchemyOrderRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = OrderService(order_repo=order_repo, product_repo=product_repo)

        orders = svc.get_all_orders()
        return jsonify(svc.orders_to_list(orders)), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()

@order_bp.get("/my")
def get_my_orders():
    db = get_db()
    try:
        auth = request.headers.get("Authorization", "")
        parts = auth.split(" ")

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise UnauthorizedError("missing or invalid authorization header")

        token = parts[1].strip()
        claims = decode_access_token(token)

        user_repo = SQLAlchemyUserRepository(db)

        sub = str(claims.get("sub") or "").strip()
        phone = str(claims.get("phone") or "").strip()

        user = None

        if sub.isdigit():
            user = user_repo.get_by_id(int(sub))

        if not user and phone:
            user = user_repo.get_by_phone(phone)

        if not user:
            raise UnauthorizedError("user not found")

        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        order_repo = SQLAlchemyOrderRepository(db)
        product_repo = SQLAlchemyProductRepository(db)
        svc = OrderService(order_repo=order_repo, product_repo=product_repo)

        orders = svc.list_by_user(user_id=int(user.id), limit=limit, offset=offset)
        return jsonify(svc.orders_to_list(orders)), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
