import smtplib, ssl
from datetime import datetime, timezone, timedelta
class Mailer():

    def __init__(self):

        self.port = 465
        self.context = ssl.create_default_context()

        self.sender_email = "fillsanzllc@gmail.com"
        self.password = "FuckFelipe247"

        self.receiver_email = "ddager16@gmail.com"


    def get_shipping_info(self, order):
        if order.get("shipping_address") is not None:
            shipping_address = order["shipping_address"]
        else:
            shipping_address = order["billing_address"]

        name = shipping_address["name"]
        address = shipping_address["address1"]
        city = shipping_address["city"]
        state = shipping_address["province_code"]
        country = shipping_address["country_code"]
        zip_code = shipping_address["zip"]

        message = f"\nName: {name} \nAddress: {address}, {city}, {state}, {country}, {zip_code}"
        return message


    def craft_email(self, orders):  # order = order object
        message = "Subject: Today's Orders\n\n"

        for order in orders.values():
            timestamp, junk = order["processed_at"].split("T")
            message += f"\nOrder ID: {order['id']} \nDate Processed: {timestamp}"

            for item in order["line_items"]:
                product_id = item['product_id']
                title = item['title']
                quantity = item['quantity']
                size = item["variant_title"]

                name_id = f"\nItem Name: {title} \nProduct ID: {product_id}"
                quantity_size = f"\nQuantity: {quantity} \nsize: {size}"
                shipping_info = self.get_shipping_info(order)

                message += name_id + quantity_size + shipping_info

            message += "\n---------------------------------------------"

        return message


    def send_email(self, orders):
        message = self.craft_email(orders)
        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=self.context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, self.receiver_email, message)

        print("Email Sent!")


    def convert_timestamp(self, order):
        timestamp = order["processed_at"]
        ts_format = "%Y-%m-%dT%H:%M:%S%z"
        ts_object = datetime.strptime(timestamp, ts_format)
        return ts_object
