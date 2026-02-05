# app/interfaces/http/controllers/admin_controller
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.blog_sqlalchemy import SQLAlchemyBlogRepository
from app.core.exceptions import AppError
from app.domain.entities.blog_post import BlogPost
from app.interfaces.http.controllers.admin import _get_claims_or_401
import re
import html


admin_blogs_bp = Blueprint("admin_blogs", __name__)


_TAG_RE = re.compile(r"<[^>]+>")
_HANDLEBARS_RE = re.compile(r"{{[\s\S]*?}}")
_ERT_RE = re.compile(r"<%[\s\S]*?%>")

def _unescape_recursive(s: str, max_rounds: int = 3) -> str:
    # برای حالت‌های double-escaped مثل &amp;lt;h2&amp;gt;
    prev = s
    for _ in range(max_rounds):
        cur = html.unescape(prev)
        if cur == prev:
            break
        prev = cur
    return prev

def make_excerpt(content: str, length: int = 150) -> str:
    if not content:
        return ""

    s = str(content)

    #  decode چندمرحله‌ای
    s = _unescape_recursive(s)

    #  حذف template tags
    s = _HANDLEBARS_RE.sub(" ", s)
    s = _ERT_RE.sub(" ", s)

    #  حذف HTML tags
    s = _TAG_RE.sub(" ", s)

    #  جمع کردن فاصله‌ها
    s = re.sub(r"\s+", " ", s).strip()

    if not s:
        return ""

    return s[:length] + ("..." if len(s) > length else "")


def parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)  # YYYY-MM-DD or ISO datetime
    except ValueError:
        return None


def parse_int(v) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def category_to_dict(cat) -> dict | None:
    if not cat:
        return None
    return {"id": cat.id, "name": getattr(cat, "name", None), "slug": getattr(cat, "slug", None)}


@admin_blogs_bp.post("")
def admin_create_post():
    db = get_db()
    try:
        _get_claims_or_401()

        repo = SQLAlchemyBlogRepository(db)
        data = request.get_json() or {}

        category_id = parse_int(data.get("category_id"))
        if category_id is not None:
            cat = repo.get_category_by_id(category_id)
            if not cat:
                return jsonify({"error": "کتگوری نامعتبر است"}), 400

        post = BlogPost(
            title=data["title"],
            slug=data["slug"],
            content=data.get("content"),
            excerpt=make_excerpt(data.get("content")),
            cover_image=data.get("cover_image"),
            is_published=data.get("is_published", False),
            published_at=parse_date(data.get("published_at")),
            author_name=data.get("author_name", "Admin"),
            category_id=category_id,
        )

        created = repo.create(post)

        # اگر relationship تعریف کردی: created.category
        cat_obj = getattr(created, "category", None)
        return jsonify({
            "id": created.id,
            "category_id": getattr(created, "category_id", None),
            "category": category_to_dict(cat_obj),
        }), 201

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@admin_blogs_bp.put("/<int:blog_id>")
def admin_update_post(blog_id: int):
    db = get_db()
    try:
        _get_claims_or_401()

        repo = SQLAlchemyBlogRepository(db)
        existing_post = repo.get_by_id(blog_id)
        if not existing_post:
            return jsonify({"error": "مقاله پیدا نشد"}), 404

        data = request.get_json() or {}

        if "category_id" in data:
            category_id = parse_int(data.get("category_id"))
            if category_id is not None:
                cat = repo.get_category_by_id(category_id)
                if not cat:
                    return jsonify({"error": "کتگوری نامعتبر است"}), 400
            existing_post.category_id = category_id

        existing_post.title = data.get("title", existing_post.title)
        existing_post.slug = data.get("slug", existing_post.slug)
        existing_post.content = data.get("content", existing_post.content)
        existing_post.excerpt = make_excerpt(existing_post.content)
        existing_post.cover_image = data.get("cover_image", existing_post.cover_image)
        existing_post.is_published = data.get("is_published", existing_post.is_published)
        existing_post.published_at = parse_date(data.get("published_at")) or existing_post.published_at
        existing_post.author_name = data.get("author_name", existing_post.author_name)

        updated = repo.update(existing_post)
        cat_obj = getattr(updated, "category", None)

        return jsonify({
            "id": updated.id,
            "category_id": getattr(updated, "category_id", None),
            "category": category_to_dict(cat_obj),
        }), 200

    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()


@admin_blogs_bp.get("")
def admin_list_blogs():
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyBlogRepository(db)
        blogs = repo.list_posts(is_published=None, limit=200, offset=0)

        return jsonify([
            {
                "id": b.id,
                "title": b.title,
                "slug": b.slug,
                "excerpt": b.excerpt,
                "cover_image": b.cover_image,
                "is_published": b.is_published,
                "published_at": b.published_at.isoformat() if b.published_at else None,
                "author_name": b.author_name or "نامشخص",
                "category_id": getattr(b, "category_id", None),
                "category": category_to_dict(getattr(b, "category", None)),
            }
            for b in blogs
        ])
    finally:
        db.close()


@admin_blogs_bp.get("/<int:blog_id>")
def admin_get_post(blog_id: int):
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyBlogRepository(db)
        post = repo.get_by_id(blog_id)
        if not post:
            return jsonify({"error": "مقاله پیدا نشد"}), 404

        return jsonify({
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "excerpt": post.excerpt,
            "content": post.content,
            "cover_image": post.cover_image,
            "is_published": post.is_published,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "author_name": post.author_name or "نامشخص",
            "category_id": getattr(post, "category_id", None),
            "category": category_to_dict(getattr(post, "category", None)),
        }), 200
    finally:
        db.close()


@admin_blogs_bp.delete("/<int:blog_id>")
def admin_delete_post(blog_id: int):
    try:
        _get_claims_or_401()
    except Exception:
        return jsonify({"error": "unauthorized"}), 401

    db = get_db()
    try:
        repo = SQLAlchemyBlogRepository(db)
        post = repo.get_by_id(blog_id)
        if not post:
            return jsonify({"error": "مقاله پیدا نشد"}), 404

        repo.delete(blog_id)
        return jsonify({"id": blog_id, "deleted": True}), 200
    finally:
        db.close()
