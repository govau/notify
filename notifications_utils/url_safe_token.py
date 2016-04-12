from itsdangerous import URLSafeTimedSerializer


def generate_token(payload, secret, salt):
    ser = URLSafeTimedSerializer(secret)
    return ser.dumps(payload, salt)


def check_token(token, secret, salt, max_age_seconds):
    ser = URLSafeTimedSerializer(secret)
    payload = ser.loads(token, max_age=max_age_seconds,
                        salt=salt)
    return payload
