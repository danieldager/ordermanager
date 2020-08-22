import json, requests
from datetime import datetime, timedelta

from mailman import Mailman


class OrderManager():

    def __init__(self):

        self.version = "2020-07"

        current_time = datetime.now().astimezone().replace(microsecond=0)
        self.last_time = (current_time - timedelta(1)).isoformat()

        self.new_orders = {}
        self.draft_orders = {}
        self.invoices = {}
        self.paid_orders = {}

        self.unfulfilled_orders = {}

        self.name = "fillsanzshop"
        self.key = "07fcc5c43475cd47234e63ce0ddbb5f7"
        self.password = "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"
        self.email = "fillsanzofficial@gmail.com"

        # Still need to update these with actual shop information
        self.shops = {
            "sanz-inc": {
                "id": 3894361751709,
                "email": "ddager16@gmail.com",
                "key": "97dca6b186fc5e50b769417fa3d56b27",
                "password": "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"
            },

            "proper-rhythm": {
                "id": 3894361751709,
                "email": "ddager16@gmail.com",
                "key": "11d47778cf35d1932bab756cb1c77dd7",
                "password": "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"
            },

            "kenny-greene-music": {
                "id": 3786275258525,
                "email": "kenyatgreene69@gmail.com",
                "key": "c6326d6096e6ead5c755aa9aec5cd290",
                "password": "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"
            }
        }

        self.mailman = Mailman()


    def do_everything(self):
        self.get_new_orders()
        self.make_draft_orders()
        self.send_draft_orders()
        self.send_invoices()
        # self.send_fulfillment_email()
        # print(self.paid_orders)

    # See https://shopify.dev/docs/admin-api/rest/reference/orders/order
    # for examples on how to format your param(eter)s
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

    # This method takes x orders from one shop and packages it into a dict
    # called draft_orders, of the form {order_id: draft_order}, which is then
    # inserted into the dict self.draft_orders as {name: draft_orders}
    def make_draft_orders(self):
        for name, orders in self.new_orders.items():
            draft_orders = []  # I should really consider breaking this up

            for order in orders:
                draft_order = {}

                shipping_address = order.get("shipping_address")
                if shipping_address is None:  # some test orders don't have one
                    shipping_address = order.get("billing_address")

                draft_order.update({"shipping_address": shipping_address})
                draft_order.update({"customer": {"id": self.shops[name]["id"]}})

                line_items = []
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
                    }  # eventually, we might want to include tax info here

                    line_items.append(line_item)

                draft_order.update({"line_items": line_items})

                order_id = order["id"]
                draft_order.update({"note": order_id})

                draft_orders.append({"draft_order": draft_order})

            self.draft_orders.update({name: draft_orders})


    def send_draft_orders(self):
        params = f"draft_orders.json"

        for name, draft_orders in self.draft_orders.items():
            if draft_orders is None:
                continue

            draft_order_ids = []
            for draft_order in draft_orders:
                draft_order = json.dumps(draft_order)
                draft_order = self.post_request(params, draft_order).json()
                draft_order_id = draft_order["draft_order"]["id"]
                draft_order_ids.append(draft_order_id)

            self.invoices.update({name: draft_order_ids})

        print(self.invoices)


    def send_invoices(self):
        data = {"draft_order_invoice": {}}
        for name, draft_order_ids in self.invoices.items():
            for draft_order_id in draft_order_ids:
                params = f"draft_orders/{draft_order_id}/send_invoice.json"
                invoice = self.post_request(params, data).json()

                print("\n_______________________________________")
                print(invoice)
                print("_______________________________________")





    def get_paid_orders(self):
        params = f"orders.json?updated_at_min={self.last_time}&financial_status=paid"
        self.paid_orders = self.get_request(params).json()["orders"]

        return self.paid_orders


    def get_original_orders(self):
        orders = []

        # for orders 

        order_ids = self.paid_orders["note"].split(",")
        for order_id in order_ids:
            params = f"orders/{order_id}.json"
            key = self.shops[name]["key"]
            password = self.shops[name]["password"]
            order = requests.get(
                f"https://{name}.myshopify.com/admin/api/{self.version}/{params}",
                auth=(key, password))

            orders.append(order)

        # print(orders)



    def send_fulfillment_email(self):
        message = self.mailman.send_email(self.paid_orders)
        print(message)



    def get_customers(self):
        params = f"customers.json"
        customer_list = self.get_request(params).json()
        print(customer_list)



    def unfulfilled_email(self):
        self.get_unfulfilled_orders()
        self.send_fulfillment_email()



om = OrderManager()
om.do_everything()

# om.get_paid_orders()
# print(om.paid_orders)
# om.get_original_orders()
# om.send_fulfillment_email()
