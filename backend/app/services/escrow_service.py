from app.core.db import db
from app.core.errors import ApiError
from app.models.mixins import MoneyMixin
from app.models.escrow import Escrow
from app.services.wallet_service import wallet_for
from app.services.ledger import debit, credit

FEE_BPS = 100  # 1.00% platform fee, charged to the seller on release


def create(buyer_id: int, seller_account: str, amount, title: str, commit=True) -> Escrow:
    from app.models import User
    seller = User.query.filter_by(account_number=seller_account.strip().upper()).first()
    if not seller:
        raise ApiError("Seller account number not found", 404, "seller_not_found")
    if seller.id == buyer_id:
        raise ApiError("You cannot escrow funds to yourself")
    cents = MoneyMixin.to_cents(amount)
    if cents < 1000:
        raise ApiError("Minimum escrow amount is KES 10.00")
    esc = Escrow(reference=Escrow.new_reference(), buyer_id=buyer_id,
                 seller_id=seller.id, amount_cents=cents,
                 fee_cents=(cents * FEE_BPS) // 10_000, title=title.strip())
    db.session.add(esc)
    db.session.commit() if commit else db.session.flush()
    return esc
