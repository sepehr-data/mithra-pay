# app/interfaces/http/controllers/auth_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.user_sqlalchemy import SQLAlchemyUserRepository
from app.domain.services.auth_service import AuthService
from app.domain.services.otp_service import OTPService
from app.core.exceptions import AppError

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    db = get_db()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        auth_service = AuthService(user_repo=user_repo)

        data = request.get_json() or {}
        user = auth_service.register_user(
            phone=data.get("phone"),
            email=data.get("email"),
            password=data.get("password"),
            full_name=data.get("full_name"),
        )
        return jsonify({
            "id": user.id,
            "phone": user.phone,
            "email": user.email,
            "full_name": user.full_name,
        }), 201
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@auth_bp.post("/login")
def login():
    db = get_db()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        auth_service = AuthService(user_repo=user_repo)

        data = request.get_json() or {}
        token = auth_service.login(
            phone=data.get("phone"),
            password=data.get("password"),
        )
        return jsonify({"access_token": token})
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@auth_bp.post("/request-otp")
def request_otp():
    db = get_db()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        otp_service = OTPService(user_repo=user_repo)

        data = request.get_json() or {}
        phone = data.get("phone")
        if not phone:
            return jsonify({"error": "phone is required"}), 400

        code = otp_service.send_otp(phone)
        # in production don't return code
        return jsonify({"message": "otp sent", "debug_code": code}), 200
    finally:
        db.close()


@auth_bp.post("/verify-otp")
def verify_otp():
    db = get_db()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        otp_service = OTPService(user_repo=user_repo)

        data = request.get_json() or {}
        phone = data.get("phone")
        code = data.get("code")

        if not phone or not code:
            return jsonify({"error": "phone and code are required"}), 400

        token = otp_service.verify_otp_and_issue_token(phone, code)
        return jsonify({"access_token": token}), 200
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
