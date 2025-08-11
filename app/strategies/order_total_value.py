from abc import ABC, abstractmethod

from app.models import order_item

class OrderTotalCalculationStrategy(ABC):
    @abstractmethod
    def calculate_total(self, db, order_id: int):
        pass

class RegularOrderTotalCalculation(OrderTotalCalculationStrategy):
    def calculate_total(self, db, order_id: int):
        items = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order == order_id).all()
        total = sum(item.subtotal for item in items)
        return total

class DiscountedOrderTotalCalculation(OrderTotalCalculationStrategy):
    def calculate_total(self, db, order_id: int):
        items = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order == order_id).all()
        total = sum(item.subtotal for item in items)
        total *= 0.90
        return total
