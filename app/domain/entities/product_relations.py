from sqlalchemy import Table, Column, Integer, ForeignKey
from app.infrastructure.db.base import Base

# جدول واسط Product <-> SubscriptionType
product_subscription_types = Table(
    "product_subscription_types",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("subscription_type_id", Integer, ForeignKey("subscription_types.id", ondelete="CASCADE"), primary_key=True),
)

# جدول واسط Product <-> DurationType
product_duration_types = Table(
    "product_duration_types",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("duration_type_id", Integer, ForeignKey("duration_types.id", ondelete="CASCADE"), primary_key=True),
)
