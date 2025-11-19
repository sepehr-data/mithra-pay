from flask import Blueprint, jsonify, request
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_sqlalchemy import SQLAlchemyUserRepository
from app.core.security import hash_password, decode_access_token  # your helpers

user_bp = Blueprint("user", __name__)


def _user_to_dict(user):
    return {
        "id": user.id,
        "phone": getattr(user, "phone", None),
        "name": getattr(user, "name", None),
        "last_name": getattr(user, "last_name", None),
        "email": getattr(user, "email", None),
        "birthday": getattr(user, "birthday", None),
        "sheba": getattr(user, "sheba", None),
    }


def _get_current_user_id():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except Exception:
        return None

    # adjust this based on how you create the token (sub vs user_id)
    return payload.get("sub") or payload.get("user_id")


def _get_db_session():
    """
    Works whether get_db() returns a session directly
    or a generator (yield pattern).
    """
    db = get_db()
    # if it's a generator, grab the first yielded value
    if not hasattr(db, "query"):
        db = next(db)
    return db


@user_bp.get("/me")
def get_me():
    user_id = _get_current_user_id()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    db = _get_db_session()
    try:
        repo = SQLAlchemyUserRepository(db)
        user = repo.get_by_id(user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404

        return jsonify(_user_to_dict(user)), 200
    finally:
        db.close()


@user_bp.put("/me")
def update_me():
    user_id = _get_current_user_id()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    db = _get_db_session()
    try:
        repo = SQLAlchemyUserRepository(db)
        user = repo.get_by_id(user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404

        data = request.get_json() or {}

        if "name" in data:
            user.first_name = data["name"] or None
        if "last_name" in data:
            user.last_name = data["last_name"] or None
        if "email" in data:
            user.email = data["email"] or None
        if "sheba" in data:
            user.sheba = data["sheba"] or None
        if "phone" in data:
            user.phone = data["phone"] or None
        if "birthday" in data:
            user.birthday = data["birthday"] or None

        if data.get("password"):
            user.password_hash = hash_password(data["password"])

        db.commit()
        db.refresh(user)

        return jsonify({
            "message": "profile updated",
            "user": _user_to_dict(user),
        }), 200
    finally:
        db.close()
