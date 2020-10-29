import requests
import json

from Trader.client import trader_client

import redis


class Request(trader_client.TraderRequest):
    def __init__(self, price: int, gateway_channel_id: int, return_url: str) -> None:
        super().__init__()
        self.price = price
        self.gatewayChannelId = gateway_channel_id
        self.returnUrl = return_url


class Response(trader_client.TraderResponse):
    def __init__(self, issuccess: bool, redirect_url: str) -> None:
        super().__init__()
        self.issuccess = issuccess
        self.redirectUrl = redirect_url

    def show(self):
        print("Response: ", self.issuccess, self.redirectUrl)


class AgahApi(trader_client.TraderClient):
    base_url = "https://onlineapi.agah.com/api/v2"

    def __init__(self):
        self.token = ""

        redis_host = "localhost"
        redis_port = 6379
        redis_password = ""
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    def login(self, username, password):
        user = {
            "username": username,
            "password": password
        }
        info = requests.post(self.base_url + "/user/login", user)

        if info.status_code != 200:
            raise trader_client.InvalidLoginException

        new = json.loads(info.content.decode("UTF-8"))
        print("LOGIN: ", new)
        self.token = new['token']

    def start_online_payment(self, req: Request) -> Response:
        url = self.base_url + "/request/onlinePayment"

        payload = {
            "price": req.price,
            "gatewayChannelId": req.gatewayChannelId,
            "returnUrl": req.returnUrl,
            "androidDefaultUrl": "asatrader://app/android/payments",
            "iosDefaultUrl": "shetab://ir.asax.asatrader.beta"
         }

        headers = {
            'caller-token': '38f791f2-aba8-4615-9e06-960f12a6b1d2',
            'Authorization': 'Bearer ' + self.token,
            'Access-Control-Allow-Origin': self.base_url,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response_json = json.loads(response.content.decode("UTF-8"))

        if response.status_code != 200:
            raise trader_client.PaymentErrorException

        self.redis_client.set("price", req.price)
        print(response_json)

        return response_json["redirectUrl"]

    def end_online_payment(self, req):
        x = self.redis_client.get("price")
        print(x)


if __name__ == "__main__":
    api = AgahApi()
    api.login("mihahoni", "$vDhmo9sN&X09KS494%")
    api.start_online_payment(Request(10000, 4, "https://www.google.com"))
    api.end_online_payment(1)
