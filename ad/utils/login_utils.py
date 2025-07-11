import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from ad.ad_vars import EMAIL_CODE_TTL

def generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def set_code_in_redis(email: str) -> str | None:
    code = generate_code()
    key = f'verify_code:{email}'
    if cache.get(key) is not None:
        return None
    cache.set(key, code, timeout=EMAIL_CODE_TTL)
    return code

def check_code_in_redis(email: str, code: str) -> bool:
    key = f'verify_code:{email}'
    stored_code = cache.get(key)
    if stored_code == code:
        cache.delete(key)
        return True
    return False

# def send_code_to_email(email: str, code: str) -> None:
#     send_mail(
#         "Обнаружен вход",
#         f"Ваш код подтверждения: {code}, Если вы не пытаетесь войти в аккаунт, советуем сменить пароль.",
#         "chempion2006vtf@gmail.com",
#         [email],
#         fail_silently=False,
#     )
