from sqlalchemy.exc import IntegrityError
from app.core.db import db
from .common import load, require
from . import participation, work, booking, extensions, cancellation, disputes

ACTIONS = {
    'accept': participation.accept, 'fund': participation.fund,
    'submit': work.submit, 'revise': work.revise, 'approve': work.approve,
    'confirm': booking.confirm, 'request-extension': extensions.request,
    'decide-extension': extensions.decide, 'cancel': cancellation.request,
    'decide-cancel': cancellation.decide, 'dispute': disputes.open_dispute,
}


def perform(eid, uid, action, data):
    require(action in ACTIONS, 'Unknown payment action', 404)
    require(isinstance(data, dict), 'Submit a JSON object', 422)
    # Each request owns one DB transaction; escrow and wallet locks prevent double settlement.
    for attempt in range(2):
        try:
            payment = load(eid, uid)
            require(payment.rules['release'] != 'delivery_code' or action == 'dispute',
                    'This website order is released only with the buyer’s delivery code')
            ACTIONS[action](payment, uid, data)
            db.session.commit()
            return payment
        except IntegrityError:
            db.session.rollback()
            if attempt:
                require(False, 'Concurrent update; refresh and try again')
        except Exception:
            db.session.rollback()
            raise
