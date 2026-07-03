from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "super-secret-key"

ALGORITHM = "HS256"

def create_access_token(data: dict,expires_minutes: int = 1440):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)

    payload.update(
        {"exp": expire}
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )