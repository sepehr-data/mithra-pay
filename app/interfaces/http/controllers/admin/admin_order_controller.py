# app/interfaces/http/controllers/admin_controller
from flask import Blueprint, request, jsonify
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.order_sqlalchemy import SQLAlchemyOrderRepository
from app.infrastructure.repositories.user_sqlalchemy import SQLAlchemyUserRepository
from app.interfaces.http.controllers.admin import _get_claims_or_401
from app.infrastructure.utils.sms_utils import send_notification
from sqlalchemy.exc import SQLAlchemyError

admin_orders_bp = Blueprint("admin_orders", __name__)


@admin_orders_bp.get("")
def admin_list_orders():
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyOrderRepository(db)
        orders = repo.get_all_orders()

        return jsonify([
            {
                "id": o.id,
                "order_number": o.order_number,
                "user_id": o.user_id,
                "status": o.status,
                "payment_status": o.payment_status,
                "admin_status": getattr(o, "admin_status", "open"),
                "total_amount": float(o.total_amount),
                "currency": o.currency,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "updated_at": o.updated_at.isoformat() if o.updated_at else None,
            }
            for o in orders
        ])

    finally:
        db.close()


@admin_orders_bp.patch("/<int:order_id>")
def update_order_admin_status(order_id: int):
    db = get_db()
    repo = SQLAlchemyOrderRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    data = request.get_json() or {}

    admin_status = data.get("admin_status")
    allowed_statuses = ["open", "pending", "closed"]
    if admin_status not in allowed_statuses:
        return jsonify({"error": "وضعیت نامعتبر"}), 400

    try:
        order = repo.get_by_id(order_id)
        if not order:
            return jsonify({"error": "سفارش مورد نظر یافت نشد."}), 404


        user = user_repo.get_by_id(order.user_id)
        if not user or not getattr(user, "phone", None):
            return jsonify({"error": "شماره موبایل کاربر یافت نشد"}), 400

        phone = user.phone

        old_status = getattr(order, "admin_status", None)
        order.admin_status = admin_status

        repo.update(order)

        if old_status == "open" and admin_status == "pending":
            send_notification(
                phone,
                pattern="order_status_in_review",
                token=f"سفارش شما در حال بررسی است. شماره سفارش: {order.order_number}"
            )
        elif admin_status == "closed":
            send_notification(
                phone,
                pattern="order_status_closed",
                token=f"سفارش شما بسته شد. شماره سفارش: {order.order_number}"
            )
        elif old_status == "closed" and admin_status == "open":
            send_notification(
                phone,
                pattern="order_status_reopened",
                token=f"سفارش شما دوباره باز شد. شماره سفارش: {order.order_number}"
            )

        return jsonify({
            "success": True,
            "message": "وضعیت سفارش به‌روزرسانی شد",
            "data": {
                "order_id": order.id,
                "order_number": order.order_number,
                "admin_status": order.admin_status
            }
        }), 200

    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({"error": "خطا در به‌روزرسانی سفارش", "details": str(e)}), 500
    finally:
        db.close()
