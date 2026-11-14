import re
from sqlalchemy import or_
from app.models import User
from app.core.errors import ApiError


def normalize(value):
    phone = re.sub(r'[\s()-]', '', str(value)).lstrip('+')
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    if not re.fullmatch(r'254[17]\d{8}', phone):
        raise ApiError('Enter a valid Kenyan mobile number, e.g. 0712345678', 422, 'invalid_phone')
    return phone


def find(phone):
    phone = normalize(phone)
    return User.query.filter(or_(User.phone == phone, User.phone == '+' + phone,
                                  User.phone == '0' + phone[3:])).first()


def require_verified(user, live=False):
    if not user or not user.is_active or not user.email_verified or not user.phone_verified:
        raise ApiError('Verify your phone number in Phone & USSD first', 403, 'phone_not_verified')
    if live and user.phone_verification_source != 'africastalking_live':
        raise ApiError('Verify this number using live SMS before using live services', 403, 'live_phone_verification_required')
    return normalize(user.phone)
