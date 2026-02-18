from flask import Blueprint, request, jsonify
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.product_sqlalchemy import SQLAlchemyProductRepository
from app.domain.entities.product import Product
from app.interfaces.http.controllers.admin import _get_claims_or_401
from app.core.exceptions import AppError
from app.domain.entities.subscription_types import SubscriptionType
from app.domain.entities.duration_types import DurationType
from app.domain.entities.product_plan_price import ProductPlanPrice

admin_products_bp = Blueprint("admin_products", __name__)


def _to_float(v):
    try:
        return float(v) if v is not None else None
    except Exception:
        return None


def _as_int_list(v):
    """accept list[int] or comma-separated string"""
    if v is None:
        return []
    if isinstance(v, list):
        out = []
        for x in v:
            try:
                out.append(int(x))
            except Exception:
                pass
        return out
    if isinstance(v, str):
        parts = [p.strip() for p in v.split(",") if p.strip()]
        out = []
        for p in parts:
            try:
                out.append(int(p))
            except Exception:
                pass
        return out
    return []


def _serialize_plan_arrays(p: Product):
    subs = []
    durs = []

    for s in getattr(p, "subscription_types", []) or []:
        subs.append({"id": s.id, "title": s.title, "slug": s.slug})

    for d in getattr(p, "duration_types", []) or []:
        durs.append({"id": d.id, "title": d.title, "slug": d.slug})

    return subs, durs


def _serialize_prices(p: Product):
    out = []
    for row in (getattr(p, "plan_prices", []) or []):
        out.append({
            "subscription_type_id": row.subscription_type_id,
            "duration_type_id": row.duration_type_id,
            "price": _to_float(row.price),
        })
    return out


def _apply_m2m_from_payload(db, p: Product, data: dict):
    touched_subs = "subscription_type_ids" in data
    touched_durs = "duration_type_ids" in data

    if touched_subs:
        ids = _as_int_list(data.get("subscription_type_ids"))
        if ids:
            p.subscription_types = (
                db.query(SubscriptionType)
                .filter(SubscriptionType.id.in_(ids))
                .all()
            )
        else:
            p.subscription_types = []

        if "personal_account" not in data:
            p.personal_account = any(st.slug == "individual" for st in (p.subscription_types or []))

    if touched_durs:
        ids = _as_int_list(data.get("duration_type_ids"))
        if ids:
            p.duration_types = (
                db.query(DurationType)
                .filter(DurationType.id.in_(ids))
                .all()
            )
        else:
            p.duration_types = []


def _apply_prices_from_payload(p: Product, data: dict):
    """
    Expect:
      prices: [
        {subscription_type_id: int, duration_type_id: int, price: number},
        ...
      ]
    """
    if "prices" not in data:
        return

    raw = data.get("prices") or []
    if not isinstance(raw, list):
        raw = []

    # map existing rows by (st_id, dt_id)
    existing = {}
    for row in (p.plan_prices or []):
        existing[(row.subscription_type_id, row.duration_type_id)] = row

    seen_keys = set()
    new_list = []

    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            st_id = int(item.get("subscription_type_id"))
            dt_id = int(item.get("duration_type_id"))
        except Exception:
            continue

        price_val = item.get("price")
        if price_val is None:
            continue

        try:
            price_val = float(price_val)
        except Exception:
            continue

        key = (st_id, dt_id)
        seen_keys.add(key)

        row = existing.get(key)
        if row is None:
            row = ProductPlanPrice(
                subscription_type_id=st_id,
                duration_type_id=dt_id,
                price=price_val,
            )
        else:
            row.price = price_val

        new_list.append(row)

    # If admin sent prices, we treat it as "replace set"
    p.plan_prices = new_list


@admin_products_bp.get("")
def admin_list_products():
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if limit <= 0 or limit > 100:
        return jsonify({"error": "limit must be between 1 and 100"}), 400
    if offset < 0:
        return jsonify({"error": "offset must be >= 0"}), 400

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)

        products = repo.list_products(is_active=None, limit=limit, offset=offset)
        total = repo.count_products()

        items = []
        for p in products:
            subs, durs = _serialize_plan_arrays(p)

            items.append({
                "id": p.id,
                "title": p.title,
                "price": _to_float(p.price),
                "is_active": p.is_active,
                "category_id": p.category_id,
                "image_url": p.image_url,
                "created_at": p.created_at.isoformat() if p.created_at else None,

                "duration_type_id": getattr(p, "duration_type_id", None),
                "subscription_type_id": getattr(p, "subscription_type_id", None),
                "personal_account": getattr(p, "personal_account", False),
                "duration": getattr(p, "duration", None),
                "subscription_type": getattr(p, "subscription_type", None),

                "subscription_types": subs,
                "duration_types": durs,

                # ✅ جدید
                "prices": _serialize_prices(p),
            })

        return jsonify({
            "items": items,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "count": len(items),
                "total": total
            }
        }), 200
    finally:
        db.close()


@admin_products_bp.post("")
def admin_create_product():
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)
        data = request.get_json() or {}

        p = Product(
            title=data.get("title"),
            slug=data.get("slug"),
            category_id=data.get("category_id"),
            price=data.get("price", 0),
            compare_at_price=data.get("compare_at_price"),
            delivery_type=data.get("delivery_type"),
            platform=data.get("platform"),

            duration_type_id=data.get("duration_type_id"),
            subscription_type_id=data.get("subscription_type_id"),

            personal_account=data.get("personal_account", False),

            duration=data.get("duration"),
            subscription_type=data.get("subscription_type"),

            region=data.get("region"),
            stock=data.get("stock"),
            is_active=data.get("is_active", True),
            image_url=data.get("image_url"),
            short_description=data.get("short_description"),
            description=data.get("description"),
        )

        _apply_m2m_from_payload(db, p, data)
        _apply_prices_from_payload(p, data)

        created = repo.create(p)
        return jsonify({"id": created.id}), 201

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@admin_products_bp.get("/<int:product_id>")
def admin_get_product(product_id: int):
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)
        p = repo.get_by_id(product_id)
        if not p:
            return jsonify({"error": "not found"}), 404

        subs, durs = _serialize_plan_arrays(p)

        payload = {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "category_id": p.category_id,
            "price": _to_float(p.price),
            "compare_at_price": _to_float(p.compare_at_price),
            "delivery_type": p.delivery_type,
            "platform": p.platform,

            "duration_type_id": getattr(p, "duration_type_id", None),
            "subscription_type_id": getattr(p, "subscription_type_id", None),
            "personal_account": getattr(p, "personal_account", False),
            "duration": getattr(p, "duration", None),
            "subscription_type": getattr(p, "subscription_type", None),

            "region": p.region,
            "stock": p.stock,
            "is_active": p.is_active,
            "image_url": p.image_url,
            "short_description": p.short_description,
            "description": p.description,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,

            "subscription_types": subs,
            "duration_types": durs,

            # ✅ جدید
            "prices": _serialize_prices(p),
        }

        dt_legacy = getattr(p, "duration_type_legacy", None) or getattr(p, "duration_type", None)
        if dt_legacy is not None:
            payload["duration_type"] = {"id": dt_legacy.id, "title": dt_legacy.title, "slug": dt_legacy.slug}

        st_legacy = getattr(p, "subscription_type_legacy", None) or getattr(p, "subscription_type_rel", None)
        if st_legacy is not None:
            payload["subscription_type_rel"] = {"id": st_legacy.id, "title": st_legacy.title, "slug": st_legacy.slug}

        return jsonify(payload), 200
    finally:
        db.close()


@admin_products_bp.put("/<int:product_id>")
def admin_update_product(product_id: int):
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyProductRepository(db)
        p = repo.get_by_id(product_id)
        if not p:
            return jsonify({"error": "not found"}), 404

        data = request.get_json() or {}

        p.title = data.get("title", p.title)
        p.slug = data.get("slug", p.slug)
        p.category_id = data.get("category_id", p.category_id)
        p.price = data.get("price", p.price)
        p.compare_at_price = data.get("compare_at_price", p.compare_at_price)
        p.delivery_type = data.get("delivery_type", p.delivery_type)
        p.platform = data.get("platform", p.platform)

        if "duration_type_id" in data:
            p.duration_type_id = data.get("duration_type_id")
        if "subscription_type_id" in data:
            p.subscription_type_id = data.get("subscription_type_id")

        if "personal_account" in data:
            p.personal_account = data.get("personal_account")

        if "duration" in data:
            p.duration = data.get("duration")
        if "subscription_type" in data:
            p.subscription_type = data.get("subscription_type")

        p.region = data.get("region", p.region)
        p.stock = data.get("stock", p.stock)
        p.is_active = data.get("is_active", p.is_active)
        p.image_url = data.get("image_url", p.image_url)
        p.short_description = data.get("short_description", p.short_description)
        p.description = data.get("description", p.description)

        _apply_m2m_from_payload(db, p, data)
        _apply_prices_from_payload(p, data)

        updated = repo.update(p)
        return jsonify({"id": updated.id}), 200
    finally:
        db.close()
