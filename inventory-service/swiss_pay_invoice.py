import json
from datetime import datetime
from collections import defaultdict

import requests
import random
import string

import utils
import total_fee_income

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# amount_in_satoshis, description, email, redirect_url, webhook_url
def create_invoice(apiKey, title, description, amount_in_satoshis, email):

    url = "https://api.swiss-bitcoin-pay.ch/checkout"

    payload = json.dumps({
        "title": title,
        "description": description,
        "amount": amount_in_satoshis,
        "unit": "sat",
        "onChain": False,
        "delay": 10, # default value
        "email": email,
        "emailLanguage": "en",
        # "redirect": True,
        # "redirectAfterPaid": "https://example.com/order/3",
        # "webhook": "https://example.com/webhook/3",
        # "extra": {
        #     "customNote": "Custom note 3",
        #     "customDevice": "Device  3",
        #     "AnyValue": None
        # }
        
        "redirect": False,
        "redirectAfterPaid": None,
        "webhook": None,
        "extra": None
    })

    headers = {
        'Content-Type': 'application/json',
        'api-key': apiKey
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response)
    # print(response.text)

    # print(response.json())

    return response.json()

def pay_invoice(nodeRestUrl, rune, invoice):
    rpc_method = "v1/pay"

    url = "%s/%s" % (nodeRestUrl, rpc_method)

    payload = { "bolt11": invoice }
    headers = {
        "content-type": "application/json",
        "Rune": rune
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def execute(hours):
    settings_data = utils.get_settings_data()

    apiKey = settings_data['apiKey']
    rune = settings_data['rune']
    nodeRestUrl = settings_data['nodeRestUrl']

    result = total_fee_income.execute(hours=hours)

    title = "Order #3"
    description = "Sample order description #3"
    amount_in_satoshis = result['channel']['total']
    email = settings_data['email']

    print("Amount in satoshis: ", amount_in_satoshis)

    result = create_invoice(apiKey, title, description, amount_in_satoshis, email)

    invoice = result['pr']

    return pay_invoice(nodeRestUrl, rune, invoice)


if __name__ == "__main__":

    settings_data = utils.get_settings_data()

    apiKey = settings_data['apiKey']
    rune = settings_data['rune']
    nodeRestUrl = settings_data['nodeRestUrl']

    title = "Order #3"
    description = "Sample order description #3"
    amount_in_satoshis = 500000
    email = settings_data['email']
    # For testing purpose, if you run this file directly
    result = create_invoice(apiKey, title, description, amount_in_satoshis, email)

    invoice = result['pr']

    pay_invoice(nodeRestUrl, rune, invoice)