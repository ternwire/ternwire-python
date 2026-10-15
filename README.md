# Ternwire Python SDK

Python client for the Ternwire transactional email API. Requires Python 3.10+
and has no runtime dependencies.

## Install

```sh
pip install ternwire
```

## Usage

```python
import os
from ternwire import TernwireApiError, TernwireClient, verify_webhook

client = TernwireClient(
    os.environ["TERNWIRE_API_KEY"],
    os.environ["TERNWIRE_API_ORIGIN"],
    timeout=30,
)
try:
    message = client.submit_email({
        "from": "notifications@your-verified-domain.com",
        "to": ["recipient@example.com"],
        "subject": "Your receipt",
        "text": "Thanks for your order.",
    }, "order-123-receipt")
    print(message)
except TernwireApiError as error:
    print(error.status, error.body, error.headers)
```

The synchronous client exposes all 17 operations using snake_case names, such as
`get_message(id)`, `create_sending_domain({"domain": "example.com"})`, and
`list_email_templates()`. Bodies and responses are dictionaries with camelCase
JSON keys. Template deletion returns `None`. Network failures use urllib exceptions.
`list_email_templates(cursor=None, limit=None)` returns one page of summaries;
pass the previous `page.nextCursor` as `cursor` to fetch the next page.

For webhooks, call `verify_webhook(signature_header, raw_body_bytes, signing_secret)`.
The optional fourth argument is the timestamp tolerance in seconds, default 300.

Set `TERNWIRE_API_KEY`, `TERNWIRE_API_ORIGIN`, `TERNWIRE_FROM`, and `TERNWIRE_TO`
before deliberately running `python3 examples/send.py`. It submits an email.

Use `https://ternwire.com` as the API origin. Read the full documentation at
[ternwire.com/docs](https://ternwire.com/docs), or contact support@ternwire.com.
Released under the MIT License.
