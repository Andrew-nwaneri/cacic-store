from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Text, Boolean, ForeignKey
from flask_login import UserMixin


# --- Base class for declarative models ---
class Base(DeclarativeBase):
    pass


# --- SQLAlchemy instance ---
db = SQLAlchemy(model_class=Base)


# --- User model ---
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    cart: Mapped[list["Cart"]] = relationship("Cart", back_populates="user", cascade="all, delete-orphan")


# --- Items model ---
class Items(db.Model):
    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(1250))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(250), nullable=False)

    cart: Mapped[list["Cart"]] = relationship("Cart", back_populates="product", cascade="all, delete-orphan")


# --- Cart model ---
class Cart(db.Model):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("stock.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="cart")
    product: Mapped["Items"] = relationship("Items", back_populates="cart")
