# app/main.py
from flask import Flask, jsonify
from flask_cors import CORS

from app.core.config import settings
from app.core.exceptions import AppError
from app.infrastructure.db.session import engine
from app.infrastructure.db.base import Base
from app.interfaces.http.routes import register_routes

FRONTEND_ORIGIN = 'http://localhost:5173'

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    # CORS(app, resources={r"/auth/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
    CORS(
        app,
        resources={
            r"/auth/*": {"origins": FRONTEND_ORIGIN},
            r"/users/*": {"origins": FRONTEND_ORIGIN},  # 👈 add this
            r"/products/*": {"origins": FRONTEND_ORIGIN},
            r"/orders/*": {"origins": FRONTEND_ORIGIN},
            r"/blog/*": {"origins": FRONTEND_ORIGIN},
            r"/admin/*": {"origins": FRONTEND_ORIGIN},
            r"/cart/*": {"origins": FRONTEND_ORIGIN},
        },
        supports_credentials=True,
    )

    # -----------------------------
    # IMPORT ALL MODELS HERE
    # so SQLAlchemy knows about them before create_all()
    # -----------------------------
    from app.domain.entities.user import User
    from app.domain.entities.role import Role
    from app.domain.entities.user_role import UserRole
    from app.domain.entities.category import Category
    from app.domain.entities.product import Product
    from app.domain.entities.order import Order
    from app.domain.entities.order_item import OrderItem
    from app.domain.entities.cart import Cart
    from app.domain.entities.cart_item import CartItem
    from app.domain.entities.payment import Payment
    from app.domain.entities.blog_post import BlogPost
    from app.domain.entities.setting import Setting
    # (add any other entity files you create later)

    # -----------------------------
    # CREATE TABLES (DEV)
    # -----------------------------
    Base.metadata.create_all(bind=engine)

    # -----------------------------
    # REGISTER ROUTES
    # -----------------------------
    register_routes(app)

    # -----------------------------
    # ERROR HANDLERS
    # -----------------------------
    @app.errorhandler(AppError)
    def handle_app_error(err: AppError):
        resp = jsonify(err.to_dict())
        resp.status_code = err.status_code
        return resp

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "not_found", "message": "resource not found"}), 404

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"error": "server_error", "message": "internal server error"}), 500

    @app.get("/")
    def root():
        return jsonify({
            "app": "MithraPay backend",
            "status": "ok",
            "env": settings.ENV,
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
