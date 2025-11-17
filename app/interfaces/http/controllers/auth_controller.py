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
    """
    Register a user with phone (and optional email/full_name).
    No password-based login in this app.
    After register, the client should call /auth/request-otp and /auth/verify-otp.
    """
    db = get_db()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        auth_service = AuthService(user_repo=user_repo)

        data = request.get_json() or {}
        print(data)
        user = auth_service.register_user(
            phone=data.get("phone"),
            email=data.get("email"),
            password=None,  # we ignore password for this flow
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


# OPTIONAL: if someone still calls /auth/login, tell them it's not allowed
@auth_bp.post("/login")
def login_disabled():
    return jsonify({
        "error": "password_login_disabled",
        "message": "This API uses OTP-only authentication. Use /auth/request-otp and /auth/verify-otp."
    }), 405


@auth_bp.post("/request-otp")
def request_otp():
    """
    Step 1: client sends phone, we generate OTP and store in Redis.
    Same for normal users and admin users — difference is only in DB roles.
    """
    db = get_db()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        otp_service = OTPService(user_repo=user_repo)

        data = request.get_json() or {}
        phone = data.get("phone")
        if not phone:
            return jsonify({"error": "phone is required"}), 400

        code = otp_service.send_otp(phone)
        # NOTE: don't return code in production
        return jsonify({"message": "otp sent", "debug_code": code}), 200
    finally:
        db.close()


@auth_bp.post("/verify-otp")
def verify_otp():
    """
    Step 2: client sends phone + code.
    If code is valid, we:
      - ensure user exists
      - update is_phone_verified = True
      - issue JWT that includes roles from DB
    So if this phone belongs to an admin (user_roles -> admin), JWT will have roles=["admin"].
    """
    db = get_db()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        otp_service = OTPService(user_repo=user_repo)

        data = request.get_json() or {}
        phone = data.get("phone")
        code = data.get("code")
        code = code[::-1]

        if not phone or not code:
            return jsonify({"error": "phone and code are required"}), 400

        token = otp_service.verify_otp_and_issue_token(phone, code)
        return jsonify({"access_token": token}), 200
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
