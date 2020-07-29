import json
import requests


class OrderManager():

    def __init__(self):

        self.version = "2020-07"

        self.unfulfilled_orders = {}
        self.unpaid_orders = {}

        self.shops = {
            "sanz-inc": {
                "key": "97dca6b186fc5e50b769417fa3d56b27",
                "password": "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"
            },

            "proper-rhythm": {
                "key": "11d47778cf35d1932bab756cb1c77dd7",
                "password": "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"
            }
        }


    def label_orders(self, orders):  # pairs orders with their ids
        labeled_orders = {}
        for order in orders:
            order_id = order["id"]
            labeled_orders.update({order_id: order})
        return labeled_orders

    # Maybe write a function that makes API calls?

    def get_unfulfilled_orders(self, shops="all"):  # grabs all unfulfilled orders

        fields = "orders.json?fulfillment_status=unfulfilled"

        if shops == "all":

            for name, credentials in self.shops.items():
                orders = requests.get(
                    f"https://{name}.myshopify.com/admin/api/{self.version}/{fields}",
                    auth=(credentials["key"], credentials["password"]))

                orders = orders.json()["orders"]
                labeled_orders = self.label_orders(orders)
                self.unfulfilled_orders.update(labeled_orders)

            print(self.unfulfilled_orders)

        # need to write an else case and a try block

    def list_order_ids(orders):
        for order_id in orders.keys():
            print(order_id)

