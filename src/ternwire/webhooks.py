import hashlib
import hmac
import math
import re
import time


def verify_webhook(header: str, body: bytes, secret: str, tolerance_seconds: float = 300) -> bool:
    """Verify the ternwire-signature header against the unmodified request bytes."""
    if not secret or not math.isfinite(tolerance_seconds) or tolerance_seconds < 0:
        return False
    match = re.fullmatch(r"\s*t=([1-9][0-9]{0,11})\s*,\s*v1=([a-f0-9]{64})\s*", header)
    if not match or abs(int(time.time()) - int(match[1])) > tolerance_seconds:
        return False
    expected = hmac.new(secret.encode("utf-8"), match[1].encode("ascii") + b"." + body,
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, match[2])
