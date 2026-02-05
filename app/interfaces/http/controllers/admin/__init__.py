from app.core.security import decode_access_token, require_roles
from flask import request

def _get_claims_or_401():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    claims = decode_access_token(token)
    # require admin
    require_roles(claims, ["admin"])
    return claims
