# app/interfaces/http/controllers/blog_controller.py
from flask import Blueprint, request, jsonify

from app.interfaces.http.controllers import get_db
from app.infrastructure.repositories.blog_sqlalchemy import SQLAlchemyBlogRepository
from app.domain.services.content_service import ContentService
from app.core.exceptions import AppError

blog_bp = Blueprint("blog", __name__)


@blog_bp.get("/")
def list_posts():
    db = get_db()
    try:
        repo = SQLAlchemyBlogRepository(db)
        svc = ContentService(blog_repo=repo)
        posts = svc.list_posts(limit=50)
        return jsonify([svc.to_dict(p) for p in posts])
    finally:
        db.close()


@blog_bp.get("/<slug>")
def get_post(slug: str):
    db = get_db()
    try:
        repo = SQLAlchemyBlogRepository(db)
        svc = ContentService(blog_repo=repo)
        post = svc.get_post(slug)
        return jsonify(svc.to_dict(post))
    except AppError as e:
        return jsonify(e.to_dict()), e.status_code
    finally:
        db.close()
