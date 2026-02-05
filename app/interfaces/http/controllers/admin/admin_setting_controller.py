# app/interfaces/http/controllers/admin_admins_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.user_sqlalchemy import SQLAlchemyUserRepository
from app.core.exceptions import AppError
from app.interfaces.http.controllers.admin import _get_claims_or_401

admin_admins_bp = Blueprint("admin_admins", __name__)


def _clean_phone(phone: str) -> str:
    if not phone:
        return ""
    return str(phone).strip().replace(" ", "").replace("-", "")


def _validate_phone_09(phone: str) -> bool:
    return phone.startswith("09") and len(phone) == 11 and phone.isdigit()


def _user_to_admin_dto(repo: SQLAlchemyUserRepository, u) -> dict:
    role_names = repo.get_role_names(u.id)
    display_name = f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}".strip() or None
    return {
        "id": u.id,
        "name": display_name,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "phone": u.phone,
        "email": u.email,
        "roles": role_names,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "updated_at": u.updated_at.isoformat() if u.updated_at else None,
    }


@admin_admins_bp.post("")
def admin_create_admin_by_phone():
    """
    POST /admin/admins
    body: { "phone": "09xxxxxxxxx" }
    """
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyUserRepository(db)
        data = request.get_json() or {}

        phone = _clean_phone(data.get("phone", ""))
        if not _validate_phone_09(phone):
            return jsonify({"error": "شماره تلفن نامعتبر است (فرمت صحیح: 09xxxxxxxxx)"}), 400

        try:
            user = repo.set_admin_by_phone(phone)
        except RuntimeError as e:
            if str(e) == "user_not_found":
                return jsonify({"error": "کاربر با این شماره پیدا نشد"}), 404
            raise

        return jsonify({"ok": True, "admin": _user_to_admin_dto(repo, user)}), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@admin_admins_bp.delete("")
def admin_remove_admin_by_phone():
    """
    DELETE /admin/admins
    body: { "phone": "09xxxxxxxxx" }
    """
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyUserRepository(db)
        data = request.get_json() or {}

        phone = _clean_phone(data.get("phone", ""))
        if not _validate_phone_09(phone):
            return jsonify({"error": "شماره تلفن نامعتبر است (فرمت صحیح: 09xxxxxxxxx)"}), 400

        try:
            user = repo.remove_admin_by_phone(phone)
        except RuntimeError as e:
            if str(e) == "user_not_found":
                return jsonify({"error": "کاربر با این شماره پیدا نشد"}), 404
            if str(e) == "not_admin":
                return jsonify({"error": "این کاربر ادمین نیست"}), 400
            raise

        return jsonify({"ok": True, "removed": True, "user": _user_to_admin_dto(repo, user)}), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@admin_admins_bp.get("")
def admin_list_admins():
    """
    GET /admin/admins?limit=200&offset=0
    """
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    limit = request.args.get("limit", default=200, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if limit <= 0 or limit > 200:
        return jsonify({"error": "limit must be between 1 and 200"}), 400
    if offset < 0:
        return jsonify({"error": "offset must be >= 0"}), 400

    db = get_db()
    try:
        repo = SQLAlchemyUserRepository(db)
        admins = repo.list_admin_users(limit=limit, offset=offset)

        return jsonify([
            _user_to_admin_dto(repo, u)
            for u in admins
        ]), 200

    finally:
        db.close()
