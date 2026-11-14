from sqlalchemy import func, case
from app.core.db import db
from app.models import Escrow
from app.models.protected_payment import ProtectedPayment
from .rules import CATEGORIES


def categories(uid=None, merchant=False):
    query = db.session.query(ProtectedPayment.category, ProtectedPayment.state,
        func.count(ProtectedPayment.id), func.sum(Escrow.amount_cents),
        func.sum(ProtectedPayment.released_cents), func.sum(ProtectedPayment.refunded_cents),
        func.sum(ProtectedPayment.earned_fee_cents)).select_from(ProtectedPayment).join(Escrow, Escrow.id == ProtectedPayment.escrow_id)
    if uid:
        condition = Escrow.seller_id == uid if merchant else (
            (Escrow.buyer_id == uid) | (Escrow.seller_id == uid))
        query = query.filter(condition)
    return [{'category': cat, 'label': CATEGORIES[cat], 'state': state, 'count': count,
             'amount_cents': int(total or 0), 'released_cents': int(released or 0),
             'refunded_cents': int(refunded or 0), 'fee_cents': int(fee or 0)}
            for cat, state, count, total, released, refunded, fee in query.group_by(
                ProtectedPayment.category, ProtectedPayment.state).all()]


def incoming(uid):
    amount = case((ProtectedPayment.id.isnot(None), Escrow.amount_cents -
        ProtectedPayment.released_cents - ProtectedPayment.refunded_cents -
        (Escrow.fee_cents - ProtectedPayment.earned_fee_cents)),
        else_=Escrow.amount_cents - Escrow.fee_cents)
    return db.session.query(func.coalesce(func.sum(amount), 0)).select_from(Escrow).outerjoin(
        ProtectedPayment).filter(Escrow.seller_id == uid,
                                 Escrow.status.in_(['funded', 'disputed'])).scalar()
