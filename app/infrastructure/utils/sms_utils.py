from kavenegar import *
import random
import re

api = KavenegarAPI('54623179656C6B4D4747443459324D33754D5235684D352B356C4C38466C2F743445346C696B393348436B3D')

def send_otp_message(phone, otp, pattern):
    try:
        params = {
            'receptor': phone,
            'template': pattern,
            'token': otp,
            'type': 'sms'
        }
        response = api.verify_lookup(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def send_notification(phone, pattern, token):
    try:

        """
        # کد واقعی ارسال پیامک هنوز غیرفعال است
        params = {
            'receptor': phone,
            'template': pattern,
            'token': token,
            'type': 'sms'
        }
        response = api.verify_lookup(params)
        print(response)
        """

        print(f"[TEST] پیامک به {phone} با قالب '{pattern}' و مقدار token='{token}' آماده ارسال است.")

    except Exception as e:
        print(f"[ERROR] {e}")


def normalize_phone(raw_phone: str) -> str:

    digits = re.sub(r'\D', '', raw_phone or '')
    if digits.startswith('0'):
        digits = digits[1:]
    if not digits.startswith('98'):
        digits = '98' + digits
    return digits

def generate_code(cnt):
    digits = "0123456789"
    random_string = "".join(random.choice(digits) for _ in range(cnt))
    return random_string
