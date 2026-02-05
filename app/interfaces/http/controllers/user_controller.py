# app/interfaces/http/controllers/user_controller.py
from flask import Blueprint, jsonify, request
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.user_sqlalchemy import SQLAlchemyUserRepository
from app.domain.services.user_service import UserService
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedError, AppError

user_bp = Blueprint("user", __name__)

def _get_current_user_id():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError("missing or invalid authorization header")

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except Exception:
        raise UnauthorizedError("invalid token")

    # adjust based on how you create your token (sub vs user_id)
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise UnauthorizedError("invalid token payload")
    return int(user_id)

@user_bp.get("/me")
def get_me():
    db = get_db()
    try:
        user_id = _get_current_user_id()
        repo = SQLAlchemyUserRepository(db)
        svc = UserService(user_repo=repo)

        user = svc.get_user(user_id)
        return jsonify(svc.to_dict(user)), 200
    except UnauthorizedError as e:
        return jsonify({"error": str(e)}), 401
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()

@user_bp.put("/me")
def update_me():
    db = get_db()
    try:
        user_id = _get_current_user_id()
        repo = SQLAlchemyUserRepository(db)
        svc = UserService(user_repo=repo)

        data = request.get_json() or {}

        # Clean payload: remove undefined/empty password
        cleaned = {k: v for k, v in data.items() if v is not None and (k != "password" or (v and v.strip()))}

        user = svc.update_user(user_id, cleaned)

        return jsonify({
            "message": "profile updated",
            "user": svc.to_dict(user),
        }), 200
    except UnauthorizedError as e:
        return jsonify({"error": str(e)}), 401
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
