import json, requests
from datetime import datetime, timezone, timedelta

from mailer import Mailer

# OM: OrderManager
class OM():

    def __init__(self):

        self.version = "2020-07"

        # don't forget to convert to string with .isoformat()
        self.current_time = datetime.now().astimezone().replace(microsecond=0)
        # self.last_sweep_at = self.current_time - timedelta(1)
        self.last_sweep_at = "2020-08-08T18:56:45-04:00"

        self.new_orders = {}
        self.unfulfilled_orders = {}

        self.main = {
            "name": "fillsanzshop",
            "email": "fillsanzofficial@gmail.com",
            "key": "07fcc5c43475cd47234e63ce0ddbb5f7",
            "password": "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"
        }

        self.shops = {
            "sanz-inc": {
                "email": "ddager16@gmail.com",
                "key": "97dca6b186fc5e50b769417fa3d56b27",
                "password": "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"
            },

            "proper-rhythm": {
                "email": "ddager16@gmail.com",
                "key": "11d47778cf35d1932bab756cb1c77dd7",
                "password": "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"
            }
        }

        self.mailer = Mailer()


    def get_new_orders(self):
        # should I just call .isoformat() in the __init__ method?
        date_str = self.last_sweep_at  # .isoformat()
        params = f"{self.version}/orders.json?updated_at_min={date_str}"

        for name, credentials in self.shops.items():
            order_list = requests.get(
                f"https://{name}.myshopify.com/admin/api/{params}",
                auth=(credentials["key"], credentials["password"]))

            order_list = order_list.json()["orders"]  # converts json to dict
            self.new_orders.update({name: order_list})


    def get_product(self, title):  # wtf is going on with these lists?
        params = f"{self.version}/products.json?title={title}"
        product = requests.get(
            f"https://{self.main['name']}.myshopify.com/admin/api/{params}",
            auth=(self.main["key"], self.main["password"]))

        return product.json()["products"][0]


    def get_product_list(self, order):
        product_list = []
        for item in order["line_items"]:
            title = item["title"]
            variant_title = item["variant_title"]
            quantity = item["quantity"]

            product = self.get_product(title)
            for variant in product["variants"]:
                if variant["title"] == variant_title:
                    variant_id = variant["id"]

            line_item = {
                "variant_id": variant_id,
                "quantity": quantity
            }

            product_list.append(line_item)

        return product_list


    def get_order_info(self, order):
        pass



    def draft_order(self, order):
        data = {
            "draft_order": {}
        }

        print(order)

        product_list = self.get_product_list(order)
        data.update({"draft_order": {"line_items": product_list}})

        data = json.dumps(data)


        self.simple_draft_order(data)






    def simple_draft_order(self, order):
        params = f"{self.version}/draft_orders.json"
        headers = {"Content-Type": "application/json"}

        request = requests.post(
            f"https://{self.main['name']}.myshopify.com/admin/api/{params}",
            auth=(self.main["key"], self.main["password"]),
            headers=headers, data=order)

        print(request.json())









    def send_invoices(self):
        for name, order_list in self.new_orders:
            key = self.shop["name"]["key"]
            password = self.shop["name"]["password"]

            for order in order_list:
                product_list = self.get_product_list(orders)

            # This is where our POST request should go


    def label_orders(self, orders):  # {order_id: order_data}
        labeled_orders = {}
        for order in orders:
            order_id = order["id"]
            labeled_orders.update({order_id: order})
        return labeled_orders


    def get_unfulfilled_orders(self, shops="all"):  # grabs all unfulfilled orders
        parameters = "orders.json?fulfillment_status=unfulfilled"
        self.get_request(parameters, shops)


    def send_fulfillment_email(self):
        message = self.mailer.send_email(self.unfulfilled_orders)
        print(message)


    def unfulfilled_email(self):
        self.get_unfulfilled_orders()
        self.send_fulfillment_email()


    def print_order_ids(self, orders):
        for order in orders.values():
            print(order["id"])





om = OM()
om.get_new_orders()

for order in om.new_orders["sanz-inc"]:
    om.draft_order(order)
