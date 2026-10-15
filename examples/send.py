import os

from ternwire import TernwireClient

client = TernwireClient(os.environ["TERNWIRE_API_KEY"], os.environ.get("TERNWIRE_API_ORIGIN"))
accepted = client.submit_email({
    "from": os.environ["TERNWIRE_FROM"],
    "to": [os.environ["TERNWIRE_TO"]],
    "subject": "Your receipt",
    "text": "Thanks for your order.",
}, "order-123-receipt")
print(accepted)
if accepted:
    print(client.get_message(accepted["id"]))
