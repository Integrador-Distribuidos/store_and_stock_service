from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.database import Base
class Stock(Base):
    __tablename__ = "stock"
    
    id_stock = Column(Integer, primary_key=True, index=True)
    id_store = Column(Integer, index=True)
    name = Column(String, index=True)
    city = Column(String, index=True)
    uf = Column(String, index=True)
    zip_code = Column(String, index=True)
    address = Column(String, index=True)
    creation_date = Column(Date, nullable=False)
    created_by = Column(Integer, nullable=False)

    products = relationship(
        "Product",
        back_populates="stock",
        cascade="all, delete-orphan"  # Remove os produtos se o estoque for deletado
    )

class Product(Base):
    __tablename__ = "product"
    
    id_product = Column(Integer, primary_key=True, index=True)
    id_stock = Column(Integer, ForeignKey("stock.id_stock", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True)
    image = Column(String)
    description = Column(String, index=True)
    price = Column(Float, index=True)
    sku = Column(String, index=True)
    category = Column(String, index=True)
    quantity = Column(Integer, index=True)
    creation_date = Column(Date, nullable=False)
    created_by = Column(Integer, nullable=False)

    # Produto pertence a um estoque (relacionamento filho)
    stock = relationship("Stock", back_populates="products")

class StockMovement(Base):
    __tablename__ = "stock_movement"
    id_movement = Column(Integer, primary_key=True, index=True)
    id_product = Column(Integer, ForeignKey("product.id_product"))
    id_stock_origin = Column(Integer)
    id_stock_destination = Column(Integer)
    quantity = Column(Integer)
    observation = Column(String)
    creation_date = Column(Date, nullable=False)
    created_by = Column(Integer, nullable=False)


