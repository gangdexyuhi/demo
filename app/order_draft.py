"""Формируемый (ещё не подтверждённый) заказ — хранится только в памяти."""


class OrderDraft:
    def __init__(self):
        self.items = []
        # user_id клиента, для которого менеджер/администратор оформляет заказ;
        # None — заказ оформляется на текущего пользователя.
        self.client_id = None

    def clear(self):
        self.items = []
        self.client_id = None

    def is_empty(self):
        return not self.items

    def find(self, stock_item_id):
        for item in self.items:
            if item["stock_item_id"] == stock_item_id:
                return item
        return None

    def quantity_in_draft(self, stock_item_id):
        item = self.find(stock_item_id)
        return item["quantity"] if item else 0

    def add(self, product, stock_item, size_text, quantity):
        """Добавляет позицию; если такой размер уже есть — увеличивает количество."""
        item = self.find(stock_item["stock_item_id"])
        if item:
            item["quantity"] += quantity
            item["available"] = stock_item["quantity_available"]
            return
        self.items.append({
            "stock_item_id": stock_item["stock_item_id"],
            "product_name": product["product_name"],
            "manufacturer_name": product["manufacturer_name"],
            "size_text": size_text,
            "quantity": quantity,
            "available": stock_item["quantity_available"],
            # Цена фиксируется в момент добавления — это цена со скидкой.
            "price": product["final_price"],
        })

    def remove(self, stock_item_id):
        self.items = [item for item in self.items if item["stock_item_id"] != stock_item_id]

    def total_pairs(self):
        return sum(item["quantity"] for item in self.items)

    def total_sum(self):
        return sum(item["quantity"] * item["price"] for item in self.items)
