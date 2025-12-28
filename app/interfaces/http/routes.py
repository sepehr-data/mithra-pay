# app/interfaces/http/routes.py
from app.interfaces.http.controllers.auth_controller import auth_bp
from app.interfaces.http.controllers.user_controller import user_bp
from app.interfaces.http.controllers.product_controller import product_bp
from app.interfaces.http.controllers.order_controller import order_bp
from app.interfaces.http.controllers.blog_controller import blog_bp
from app.interfaces.http.controllers.admin_controller import admin_bp
from app.interfaces.http.controllers.cart_controller import cart_bp


def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(product_bp, url_prefix="/products")
    app.register_blueprint(order_bp, url_prefix="/orders")
    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(cart_bp, url_prefix="/cart")
