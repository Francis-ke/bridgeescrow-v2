import hashlib
from flask import current_app, g
from app.services import ussd_helpers as h
from app.services.mpesa_collection import initiate


def deposit(phone, steps):
    if len(steps) == 1:
        return 'CON Enter deposit amount in whole KES'
    if current_app.config['PAYMENT_MODE'] == 'simulated':
        return 'END Simulated payments only. Open Deposit on the website to test a top-up.'
    user = h.user_by_phone(phone)
    key = 'ussd-' + hashlib.sha256(g.ussd_session_id.encode()).hexdigest()
    pay = initiate(user.id, steps[1], key)
    return f'END M-PESA request recorded for {pay.msisdn}. Confirm any prompt on your phone. Ref {pay.reference}. Credit waits for provider confirmation.'
