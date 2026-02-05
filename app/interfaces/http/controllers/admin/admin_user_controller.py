# app/interfaces/http/controllers/admin_controller
from flask import Blueprint, request, jsonify
from app.core.exceptions import ValidationError
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.user_sqlalchemy import SQLAlchemyUserRepository
from app.core.security import decode_access_token, require_roles
from app.interfaces.http.controllers.admin import _get_claims_or_401

admin_users_bp = Blueprint("admin_users", __name__)


@admin_users_bp.get("")
def get_all_users():
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if limit <= 0 or limit > 100:
        raise ValidationError("limit must be between 1 and 100")
    if offset < 0:
        raise ValidationError("offset must be >= 0")

    db = get_db()
    repo = SQLAlchemyUserRepository(db)

    users = repo.list_users(limit=limit, offset=offset)
    total = repo.count_users()

    return jsonify({
        "items": [
            {
                "id": user.id,
                "email": user.email,
                "full_name": " ".join(filter(None, [user.first_name, user.last_name])).strip() or None,
                "phone": user.phone,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "count": len(users),
            "total": total
        }
    }), 200

