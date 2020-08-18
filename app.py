import json, requests
from datetime import datetime, timedelta

from mailer import Mailer


class OrderManager():

    def __init__(self):

        self.version = "2020-07"

        current_time = datetime.now().astimezone().replace(microsecond=0)
        self.last_time = (current_time - timedelta(1)).isoformat()

        self.new_orders = {}
        self.paid_orders = {}

        self.unfulfilled_orders = {}

        self.name = "fillsanzshop"
        self.key = "07fcc5c43475cd47234e63ce0ddbb5f7"
        self.password = "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"
        self.email = "fillsanzofficial@gmail.com"

        self.shops = {
            "sanz-inc": {
                "id": 3894361751709,
                "email": "dager.verde@gmail.com",
                "key": "97dca6b186fc5e50b769417fa3d56b27",
                "password": "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"
            },

            "proper-rhythm": {
                "email": "ddager16@gmail.com",
                "key": "11d47778cf35d1932bab756cb1c77dd7",
                "password": "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"
            },
            
            "kenny-greene-music": {
                "email": "kennygreenelionslead@gmail.com",
                "key": "c6326d6096e6ead5c755aa9aec5cd290",
                "password": "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"
            }
        }

        self.mailer = Mailer()


    def do_everything(self):
        self.get_new_orders()
        self.send_invoices()
        self.get_paid_orders()


    def get_request(self, params):
        request = requests.get(
            f"https://{self.name}.myshopify.com/admin/api/{self.version}/{params}",
            auth=(self.key, self.password))

        return request

    def post_request(self, params, data):
        headers = {"Content-Type": "application/json"}
        request = requests.post(
            f"https://{self.name}.myshopify.com/admin/api/{self.version}/{params}",
            auth=(self.key, self.password),
            headers=headers, data=data)

        return request



    def get_new_orders(self):
        params = f"orders.json?updated_at_min={self.last_time}"

        for name, credentials in self.shops.items():
            order_list = requests.get(
                f"https://{name}.myshopify.com/admin/api/{self.version}/{params}",
                auth=(credentials["key"], credentials["password"]))

            order_list = order_list.json()["orders"]  # converts json to dict
            self.new_orders.update({name: order_list})


    def get_product(self, title):  # wtf is going on with these lists?
        params = f"products.json?title={title}"
        product = self.get_request(params).json()["products"][0]

        return product


    def make_draft_order(self, order_list):
        draft_order = {}
        line_items = []
        order_ids = []

        for order in order_list:
            print(order)
            shipping_address = order["shipping_address"]
            draft_order.update({"shipping_address": shipping_address})

            order_ids.append(str(order["id"]))

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

                line_items.append(line_item)

            draft_order.update({"line_items": line_items})
            draft_order.update({"note": ",".join(order_ids)})

        return draft_order


    def send_draft_order(self, data):
        params = f"draft_orders.json"
        draft_order = self.post_request(params, data).json()
        draft_order_id = draft_order["draft_order"]["id"]
        return draft_order_id  # ugly workaround


    def send_invoice(self, id):
        params = f"draft_orders/{id}/send_invoice.json"
        data = {"draft_order_invoice": {}}

        invoice = self.post_request(params, data)
        return invoice


    def send_invoices(self):
        for name, order_list in self.new_orders.items():

            if not order_list:  # if order list is empty
                continue  # go to the next loop

            draft_order = self.make_draft_order(order_list)
            draft_order.update({"customer": {"id": self.shops[name]["id"]}})
            draft_order = {"draft_order": draft_order}
            draft_order = json.dumps(draft_order)

            draft_order_id = self.send_draft_order(draft_order)
            self.send_invoice(draft_order_id)


    def get_paid_orders(self):
        params = f"orders.json?updated_at_min={self.last_time}&financial_status=paid"
        self.paid_orders = self.get_request(params).json()["orders"]

        return self.paid_orders


    def send_fulfillment_email(self):
        message = self.mailer.send_email(self.paid_orders)
        print(message)





    def get_customers(self):
        params = f"customers.json"
        customer_list = self.get_request(params).json()
        return customer_list



    def unfulfilled_email(self):
        self.get_unfulfilled_orders()
        self.send_fulfillment_email()



om = OrderManager()
om.get_paid_orders()
print(om.paid_orders)
om.send_fulfillment_email()
