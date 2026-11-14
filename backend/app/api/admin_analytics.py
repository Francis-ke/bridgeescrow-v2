from flask import Blueprint
from sqlalchemy import func, case
from app.core.db import db
from app.core.decorators import role_required
from app.models import Escrow, Merchant, User, Payment
from app.api.admin_routes import bp as _admin_bp
from app.models.mixins import MoneyMixin

bp = _admin_bp


@bp.get("/analytics")
@role_required("admin")
def analytics():
    volumes = dict(db.session.query(Escrow.status,
                                    func.coalesce(func.sum(Escrow.amount_cents), 0))
                   .group_by(Escrow.status).all())
    from app.models.protected_payment import ProtectedPayment
    earned = case((ProtectedPayment.id.isnot(None), ProtectedPayment.earned_fee_cents),
                  (Escrow.status == 'released', Escrow.fee_cents), else_=0)
    fees = db.session.query(func.coalesce(func.sum(earned), 0)).select_from(Escrow).outerjoin(ProtectedPayment).scalar()
    from app.services.protected.reports import categories
    return {'protected_categories': categories(), "volume_cents": {k: int(v) for k, v in volumes.items()},
            "fees_earned": MoneyMixin.from_cents(int(fees or 0)),
            "customers": User.query.filter_by(role="customer").count(),
            "merchants": Merchant.query.count(),
            "payments_confirmed": Payment.query.filter_by(
                status="confirmed").count()}
