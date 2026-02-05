# app/interfaces/http/routes.py
from app.interfaces.http.controllers.auth_controller import auth_bp
from app.interfaces.http.controllers.user_controller import user_bp
from app.interfaces.http.controllers.product_controller import product_bp
from app.interfaces.http.controllers.order_controller import order_bp
from app.interfaces.http.controllers.blog_controller import blog_bp
from app.interfaces.http.controllers.admin.admin_blog_controller import admin_blogs_bp
from app.interfaces.http.controllers.admin.admin_user_controller import admin_users_bp
from app.interfaces.http.controllers.admin.admin_product_controller import admin_products_bp
from app.interfaces.http.controllers.admin.admin_banner_controller import admin_banners_bp
from app.interfaces.http.controllers.admin.admin_ticket_controller import admin_tickets_bp
from app.interfaces.http.controllers.admin.admin_order_controller import admin_orders_bp
from app.interfaces.http.controllers.banner_controller import banners_bp
from app.interfaces.http.controllers.ticket_controller import tickets_bp
from app.interfaces.http.controllers.admin.admin_setting_controller import admin_admins_bp



def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/auth", strict_slashes=False)
    app.register_blueprint(user_bp, url_prefix="/users", strict_slashes=False)
    app.register_blueprint(product_bp, url_prefix="/products", strict_slashes=False)
    app.register_blueprint(order_bp, url_prefix="/orders", strict_slashes=False)
    app.register_blueprint(blog_bp, url_prefix="/blogs", strict_slashes=False)
    app.register_blueprint(banners_bp, url_prefix="/banners", strict_slashes=False)
    app.register_blueprint(admin_blogs_bp, url_prefix="/admin/blogs", strict_slashes=False)
    app.register_blueprint(tickets_bp, url_prefix="/tickets", strict_slashes=False)
    app.register_blueprint(admin_admins_bp, url_prefix="/admin/admins", strict_slashes=False)
    app.register_blueprint(admin_tickets_bp, url_prefix="/admin/tickets", strict_slashes=False)
    app.register_blueprint(admin_users_bp, url_prefix="/admin/users", strict_slashes=False)
    app.register_blueprint(admin_banners_bp, url_prefix="/admin/banners", strict_slashes=False)
    app.register_blueprint(admin_products_bp, url_prefix="/admin/products", strict_slashes=False)
    app.register_blueprint(admin_orders_bp, url_prefix="/admin/orders", strict_slashes=False)
