# app/interfaces/http/controllers/tickets.py
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.ticket_sqlalchemy import SQLAlchemyTicketRepository
from app.infrastructure.utils.sms_utils import send_notification

admin_tickets_bp = Blueprint("admin_tickets", __name__)


@admin_tickets_bp.get("")
def get_all_tickets():
    db = get_db()
    repo = SQLAlchemyTicketRepository(db)

    try:
        tickets = repo.list()

        return jsonify([
            {
                "id": ticket.id,
                "name": ticket.name,
                "email": ticket.email,
                "phone":ticket.phone,
                "subject": ticket.subject,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            }
            for ticket in tickets
        ]), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": "خطا در دریافت لیست تیکت‌ها",
            "details": str(e)
        }), 500


@admin_tickets_bp.get("/<int:ticket_id>")
def get_ticket(ticket_id: int):
    db = get_db()
    repo = SQLAlchemyTicketRepository(db)

    try:
        ticket = repo.get_by_id(ticket_id)

        if not ticket:
            return jsonify({"error": "تیکت مورد نظر یافت نشد."}), 404

        return jsonify({
            "id": ticket.id,
            "name": ticket.name,
            "email": ticket.email,
            "phone": ticket.phone,
            "subject": ticket.subject,
            "message": ticket.message,
            "order_number": ticket.order_number,
            "status": ticket.status,
            "accepted_policy": ticket.accepted_policy,
            "user_id": ticket.user_id,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": "خطا در دریافت تیکت",
            "details": str(e)
        }), 500


@admin_tickets_bp.patch("/<int:ticket_id>")
def update_ticket(ticket_id: int):
    db = get_db()
    repo = SQLAlchemyTicketRepository(db)
    data = request.get_json() or {}

    status = data.get("status")           # open | pending | closed
    final_decision = data.get("final_decision")  # approved | rejected | None

    if status not in ["open", "pending", "closed"]:
        return jsonify({"error": "وضعیت نامعتبر"}), 400

    if status == "closed" and final_decision not in ["approved", "rejected"]:
        return jsonify({"error": "در حالت بسته شده، نتیجه درخواست باید تعیین شود"}), 400

    try:
        ticket = repo.get_by_id(ticket_id)
        if not ticket:
            return jsonify({"error": "تیکت مورد نظر یافت نشد."}), 404

        old_status = ticket.status
        ticket.status = status

        repo.update(ticket)

        if old_status == "open" and status == "pending":
            send_notification(
                ticket.phone,
                pattern="ticket_status_update",
                token=f"تیکت شما در حال بررسی است: {ticket.subject}"
            )
        elif status == "closed":
            if final_decision == "approved":
                send_notification(
                    ticket.phone,
                    pattern="ticket_status_closed",
                    token=f"تیکت شما تایید شد: {ticket.subject}"
                )
            else:
                send_notification(
                    ticket.phone,
                    pattern="ticket_status_closed",
                    token=f"تیکت شما رد شد: {ticket.subject}"
                )
        elif old_status == "closed" and status == "open":
            send_notification(
                ticket.phone,
                pattern="ticket_status_reopened",
                token=f"تیکت شما دوباره باز شد: {ticket.subject}"
            )

        return jsonify({"success": True, "message": "تیکت به‌روزرسانی شد"}), 200
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({
            "error": "خطا در به‌روزرسانی تیکت",
            "details": str(e)
        }), 500
