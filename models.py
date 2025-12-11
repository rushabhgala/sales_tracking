from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name=Column(String, unique=True, nullable=False)
    price=Column(Float, nullable=False)

    sale_logs = relationship(
        "SaleLog",
        back_populates="item",
        cascade="all, delete-orphan"
    )
class SaleLog(Base):
    __tablename__ = "sale_logs"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)

    # Link back to the menu items
    item = relationship("MenuItem", back_populates="sale_logs")