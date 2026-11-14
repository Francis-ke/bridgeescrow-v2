import secrets


def new_card_number():
    """A local virtual identifier, not a bank-issued payment card number."""
    return f"9900{secrets.randbelow(10**12):012d}"


def new_card_cvv(context):
    """Assign a persistent display code for a local virtual card."""
    from sqlalchemy import text
    codes = [f"{number:03d}" for number in range(1000) if number != 942]
    used = set(context.connection.execute(text(
        "SELECT DISTINCT card_cvv FROM users WHERE card_cvv IS NOT NULL"
    )).scalars())
    # A three-digit code has a finite namespace, so it is not a global identifier.
    available = [code for code in codes if code not in used]
    return secrets.choice(available or codes)
