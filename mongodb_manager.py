import pymongo
from datetime import date


class MongoDBManager:
    def __init__(self, link):
        """Establishing connection with database"""
        self._client = pymongo.MongoClient(link)

    def update_state(self, user_id, state):
        """Update the state of the user with the following id"""
        self._client.DarkBot.UserStates.update_one({"_id": user_id}, {"$set": {"state": state}}, upsert=True)

    def update_last_message(self, user_id, last_message_id):
        """Update the id of the last message sent by bot"""
        self._client.DarkBot.UserStates.update_one({"_id": user_id},
                                                   {"$set": {"last_message_id": last_message_id}}, upsert=True)

    def get_state(self, user_id):
        """Returns the state of the user with the following id"""
        result = self._client.DarkBot.UserStates.find_one({"_id": user_id})
        if result is None:
            return 0
        try:
            result["state"]
        except KeyError:
            return 0
        return int(result["state"])

    def get_last_message(self, user_id):
        """Returns the last bot message_id in the chat with the user with the following id"""
        result = self._client.DarkBot.UserStates.find_one({"_id": user_id})
        if result is None:
            return None
        return int(result["last_message_id"])

    def get_products(self):
        """Returns list of available products to sell"""
        return list(self._client.DarkBot.Products.find({}, {"price": 1, "_id": 1}))

    def get_product_price(self, name):
        """Return the price of the product with the following name. If it does not exist, KeyError is raised"""
        result = self._client.DarkBot.Products.find_one({"_id": name})
        if result is None:
            raise KeyError
        return int(result["price"])

    def user_exists(self, user_id):
        """Checks whether the user with the following id made an order"""
        return self._client.DarkBot.Orders.find_one({"_id": user_id}) is not None

    def update_current_order(self, user_id, product=None, amount=None):
        if amount is None and product is None:
            return
        if amount is None:
            self._client.DarkBot.UserStates.update_one({"_id": user_id},
                                                       {"$set": {"current_order": {
                                                           "product": product
                                                       }}}, upsert=True)
        if product is None:
            product = self._client.DarkBot.UserStates.find_one({"_id": user_id})["current_order"]["product"]
            self._client.DarkBot.UserStates.update_one({"_id": user_id},
                                                       {"$set": {"current_order": {
                                                           "product": product,
                                                           "amount": amount,
                                                           "date": date.today().__str__()
                                                       }}}, upsert=True)

    def get_current_order(self, user_id):
        return self._client.DarkBot.UserStates.find_one({"_id": user_id})["current_order"]

    def create_user(self, user_id, order, def_checkpoint):
        self._client.DarkBot.Orders.insert_one({"_id": user_id, "orders": [order], "checkpoint": def_checkpoint})

    def delete_user(self, user_id):
        self._client.DarkBot.Orders.delete_one({"_id": user_id})

    def get_user(self, user_id):
        return dict(self._client.DarkBot.Orders.find_one({"_id": user_id}))

    def add_order(self, user_id, order):
        self._client.DarkBot.Orders.update_one({"_id": user_id}, {"$push": {"orders": order}})

    def update_phone_number(self, user_id, phone_number):
        self._client.DarkBot.Orders.update_one({"_id": user_id}, {"$set": {"phone_number": phone_number}}, upsert=True)

    def update_email(self, user_id, email):
        self._client.DarkBot.Orders.update_one({"_id": user_id}, {"$set": {"email": email}}, upsert=True)

    def update_desires(self, user_id, desires):
        self._client.DarkBot.Orders.update_one({"_id": user_id}, {"$set": {"desires": desires}}, upsert=True)

    def check_desires(self, user_id):
        return self._client.DarkBot.Orders.find_one({"_id": user_id, "desires": {"$exists": True}}) is not None

    def get_desires(self, user_id):
        return self._client.DarkBot.Orders.find_one({"_id": user_id})["desires"]

    def get_all_orders(self, user_id):
        orders = self._client.DarkBot.Orders.find_one({"_id": user_id})
        if orders is None:
            return {}
        return orders["orders"]

    def count_total_sum(self, user_id):
        orders = self.get_all_orders(user_id)
        result = 0
        for order in orders:
            result += self.get_product_price(order["product"]) * order["amount"]
        return result

    def clear_orders(self, user_id):
        self._client.DarkBot.Orders.update_one({"_id": user_id}, {"$set": {"orders": []}})

    def set_checkpoint(self, user_id, state):
        self._client.DarkBot.Orders.update_one({"_id": user_id}, {"$set": {"checkpoint": state}})

    def get_checkpoint(self, user_id):
        result = self._client.DarkBot.Orders.find_one({"_id": user_id})
        if result is None:
            return 0
        return result["checkpoint"]
