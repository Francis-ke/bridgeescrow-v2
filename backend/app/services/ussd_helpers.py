from app.models import User, Escrow

NO_ACCOUNT = "END No account for this number. Register on the web portal first."


def user_by_phone(phone: str):
    from .phone_numbers import find
    return find(phone)


def short_escrows(user, limit: int = 3) -> str:
    rows = (Escrow.query.filter((Escrow.buyer_id == user.id) |
                                (Escrow.seller_id == user.id))
            .order_by(Escrow.id.desc()).limit(limit).all())
    if not rows:
        return "END You have no escrows yet."
    lines = [f"{e.reference} {e.to_dict()['amount']} {e.status}" for e in rows]
    return "END " + "\n".join(lines)
