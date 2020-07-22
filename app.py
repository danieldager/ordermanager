import json
import requests

shop_name = "sanz-inc"
api_version = "2020-07"
api_key = "97dca6b186fc5e50b769417fa3d56b27"
password = "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"

response = requests.get(
    f"https://{api_key}:{password}@{shop_name}.myshopify.com/admin/api/{api_version}/orders.json?status=any")

print(response.text)
