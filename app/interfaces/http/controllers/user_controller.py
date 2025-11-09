# app/interfaces/http/controllers/user_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.user_sqlalchemy import SQLAlchemyUserRepository
from app.core.exceptions import AppError

user_bp = Blueprint("users", __name__)


@user_bp.get("/me")
def get_me():
    """
    In production: read user_id from JWT.
    For now: accept ?user_id=...
    """
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id is required (temporary)"}), 400

    db = get_db()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        user = user_repo.get_by_id(user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404

        return jsonify({
            "id": user.id,
            "full_name": user.full_name,
            "phone": user.phone,
            "email": user.email,
            "is_phone_verified": user.is_phone_verified,
        })
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
