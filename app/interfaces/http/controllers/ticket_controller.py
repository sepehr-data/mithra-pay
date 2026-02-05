# app/interfaces/http/controllers/tickets.py
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.interfaces.http.controllers import get_db
from app.domain.entities.ticket import Ticket
from app.infrastructure.repositories.ticket_sqlalchemy import SQLAlchemyTicketRepository

tickets_bp = Blueprint("tickets", __name__)

@tickets_bp.post("/")
def create_ticket():

    db = get_db()
    repo = SQLAlchemyTicketRepository(db)

    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    subject = data.get("subject")
    message = data.get("message")
    order_number = data.get("orderNumber")
    accept_policy = data.get("acceptPolicy", False)
    user_id = data.get("user_id")

    if not all([name, email, phone, subject, message]):
        return jsonify({"error": "تمام فیلدهای ضروری پر نشده‌اند."}), 400

    if not accept_policy:
        return jsonify({"error": "کاربر با قوانین موافقت نکرده است."}), 400

    try:
        ticket = Ticket(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            order_number=order_number,
            accepted_policy=accept_policy,
            user_id=user_id
        )

        ticket = repo.create(ticket)

        return jsonify({
            "id": ticket.id,
            "status": ticket.status,
            "message": "تیکت با موفقیت ثبت شد."
        }), 201

    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({"error": "خطا در ثبت تیکت", "details": str(e)}), 500

