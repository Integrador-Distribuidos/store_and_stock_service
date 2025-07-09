from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from app.database import Base
class Product(Base):
    __tablename__ = "product"
    id_product = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Float, index=True)
    sku = Column(String, index=True)
    category = Column(String, index=True)
    creation_date = Column(Date, nullable=False)

class StockMovement(Base):
    __tablename__ = "stock_movement"
    id_movement = Column(Integer, primary_key=True, index=True)
    id_product = Column(Integer, ForeignKey("product.id_product"))
    id_stock_origin = Column(Integer)
    id_stock_destination = Column(Integer)
    quantity = Column(Integer)
    observation = Column(String)
    movement_type = Column(String)
    creation_date = Column(Date, nullable=False)

class ProductStock(Base):
    __tablename__ = "product_stock"
    id_productstock = Column(Integer, primary_key=True, index=True)
    id_product = Column(Integer, ForeignKey("product.id_product"), index=True)
    id_stock = Column(Integer, ForeignKey("stock.id_stock"), index=True)
    quantity = Column(Integer, index=True)
    last_update_date = Column(Date, nullable=False)

class Stock(Base):
    __tablename__ = "stock"
    id_stock = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    city = Column(String, index=True)
    uf = Column(String, index=True)
    zip_code = Column(String, index=True)
    address = Column(String, index=True)
    creation_date = Column(Date, nullable=False)