# app/interfaces/http/controllers/order_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.order_sqlalchemy import SQLAlchemyOrderRepository
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.services.order_service import OrderService
from app.core.exceptions import AppError

order_bp = Blueprint("orders", __name__)


@order_bp.post("/")
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
