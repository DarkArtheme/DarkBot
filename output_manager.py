from re import match


class IOManager:
    @staticmethod
    def get_products(products):
        """Returns a string, containing info about all available products"""
        result = ["Доступны следующие товары:"]
        for product in products:
            if "price" in product:
                result.append(f"{product['_id']} - {product['price']} RUB")
        return "\n".join(result)

    @staticmethod
    def get_products_name_list(products):
        """Returns a list, containing names of all available products"""
        return [value for product in products for key, value in product.items() if key == "_id"]

    @staticmethod
    def get_all_orders(orders, total_sum):
        if len(orders) == 0:
            return "Ваша корзина пуста."
        result = ["Ваша корзина выглядит так:"]
        for order in orders:
            result.append(f"-  {order['product']} (x{order['amount']})")
        result.append(f"Итого: {total_sum} RUB")
        return "\n".join(result)

    @staticmethod
    def check_phone_number(in_str):
        if match("\+[7]\d{10}", in_str) and len(in_str) == 12:
            return in_str[0:2] + "-" + in_str[2:5] + "-" + in_str[5:8] + "-" + in_str[8:10] + "-" + in_str[10:12]
        if match("\+[7][-]\d{3}[-]\d{3}[-]\d{2}[-]\d{2}", in_str) and len(in_str) == 16:
            return in_str
        return None

    @staticmethod
    def get_contact_info(user):
        if user == {}:
            result = ["Произошла ошибка, пользователь не найден. Пожалуйста, повторите заказ.",
                      "Приносим извинения за неудобства!"]
        else:
            result = [f"Номер телефона:\n{user['phone_number']}", f"Email:\n{user['email']}"]
        return "\n".join(result)

